import requests

def setup():
    print("Setting up Keycloak...")
    token_res = requests.post(
        "http://localhost:8080/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": "admin",
            "password": "replace-for-shared-environments",
            "grant_type": "password"
        }
    )
    if token_res.status_code != 200:
        print("Failed to authenticate with Keycloak master realm")
        return
    
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1. Get client ID
    clients = requests.get("http://localhost:8080/admin/realms/mplads/clients?clientId=mplads-dashboard", headers=headers).json()
    if not clients:
        print("Client mplads-dashboard not found!")
        return
    cid = clients[0]["id"]

    # 2. Add Hardcoded Audience Mapper for 'account'
    mapper = {
        "name": "audience mapper",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-mapper",
        "consentRequired": False,
        "config": {
            "included.client.audience": "account",
            "id.token.claim": "false",
            "access.token.claim": "true"
        }
    }
    requests.post(f"http://localhost:8080/admin/realms/mplads/clients/{cid}/protocol-mappers/models", headers=headers, json=mapper)
    print("Added audience mapper to client")

    # 3. Ensure 'officer' user exists
    users = requests.get("http://localhost:8080/admin/realms/mplads/users?username=officer", headers=headers).json()
    if not users:
        requests.post("http://localhost:8080/admin/realms/mplads/users", headers=headers, json={
            "username": "officer",
            "enabled": True,
            "credentials": [{"type": "password", "value": "password", "temporary": False}]
        })
        users = requests.get("http://localhost:8080/admin/realms/mplads/users?username=officer", headers=headers).json()
    
    if not users:
        print("Failed to create test user")
        return
    user_id = users[0]["id"]

    # 4. Give user "NationalAdmin" realm role
    roles = requests.get("http://localhost:8080/admin/realms/mplads/roles", headers=headers).json()
    admin_role = next((r for r in roles if r["name"] == "NationalAdmin"), None)
    if not admin_role:
        requests.post("http://localhost:8080/admin/realms/mplads/roles", headers=headers, json={"name": "NationalAdmin"})
        roles = requests.get("http://localhost:8080/admin/realms/mplads/roles", headers=headers).json()
        admin_role = next((r for r in roles if r["name"] == "NationalAdmin"), None)

    requests.post(f"http://localhost:8080/admin/realms/mplads/users/{user_id}/role-mappings/realm", headers=headers, json=[admin_role])
    print("Assigned NationalAdmin role to 'officer'")
    print("Keycloak setup complete!")

if __name__ == "__main__":
    setup()
