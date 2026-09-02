from dataclasses import dataclass
from functools import lru_cache
from collections.abc import Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings


@dataclass(frozen=True)
class Principal:
    id: str
    name: str
    roles: set[str]
    state: str | None = None
    district: str | None = None


bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def jwks_client() -> PyJWKClient:
    return PyJWKClient(settings.oidc_jwks_url)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    if not settings.auth_enabled:
        return Principal(
            id=settings.dev_user_id,
            name=settings.dev_user_name,
            roles={"NationalAdmin", "Auditor", "Viewer"},
        )

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        signing_key = jwks_client().get_signing_key_from_jwt(credentials.credentials)
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer_url,
        )
    except Exception as exc:
        print(f"Token validation error: {exc}", flush=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc

    roles = set(payload.get("realm_access", {}).get("roles", []))
    roles.update(payload.get("resource_access", {}).get(settings.oidc_audience, {}).get("roles", []))
    return Principal(
        id=str(payload.get("sub")),
        name=payload.get("name") or payload.get("preferred_username") or "Officer",
        roles=roles,
        state=payload.get("state"),
        district=payload.get("district"),
    )


def require_roles(*allowed_roles: str):
    def dependency(user: Principal = Depends(get_current_user)) -> Principal:
        if not user.roles.intersection(allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency


def get_scoped_db(user: Principal = Depends(get_current_user)) -> Generator[Session, None, None]:
    from app.db import SessionLocal

    session = SessionLocal()
    try:
        if settings.is_postgres:
            is_national = bool(user.roles.intersection({"NationalAdmin", "Auditor"}))
            session.execute(text("SET ROLE mplads_runtime"))
            session.execute(text("SELECT set_config('app.is_national', :value, false)"), {"value": str(is_national).lower()})
            session.execute(text("SELECT set_config('app.user_state', :value, false)"), {"value": user.state or ""})
            session.execute(text("SELECT set_config('app.user_district', :value, false)"), {"value": user.district or ""})
            session.execute(text("SELECT set_config('app.roles', :value, false)"), {"value": ",".join(sorted(user.roles))})
            session.execute(text("SELECT set_config('app.user_id', :value, false)"), {"value": user.id})
        yield session
    finally:
        if settings.is_postgres:
            try:
                session.rollback()
                session.execute(text("RESET ROLE"))
                session.execute(text("RESET app.is_national"))
                session.execute(text("RESET app.user_state"))
                session.execute(text("RESET app.user_district"))
                session.execute(text("RESET app.roles"))
                session.execute(text("RESET app.user_id"))
                session.commit()
            except Exception:
                session.rollback()
        session.close()

