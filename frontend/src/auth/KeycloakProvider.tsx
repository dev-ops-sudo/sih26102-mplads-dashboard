import React, { createContext, useContext, useEffect, useState } from 'react';
import { keycloak } from './keycloak';




interface AuthContextType {
  authenticated: boolean;
  token: string | undefined;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const KeycloakProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authenticated, setAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | undefined>(undefined);
  const [initialized, setInitialized] = useState<boolean>(false);

  useEffect(() => {
    keycloak.init({
      onLoad: 'login-required',
      checkLoginIframe: false
    })
    .then((auth) => {
      setAuthenticated(auth);
      setToken(keycloak.token);
      
      setInitialized(true);
      
      // Update token on refresh
      keycloak.onTokenExpired = () => {
        keycloak.updateToken(30).then((refreshed) => {
          if (refreshed) {
            setToken(keycloak.token);
            
          }
        }).catch(() => {
          keycloak.login();
        });
      };
    })
    .catch((error) => {
      console.error("Keycloak init error", error);
      setInitialized(true);
    });
  }, []);

  if (!initialized) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '24px' }}>Loading Authentication...</div>;
  }

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        token,
        login: () => keycloak.login(),
        logout: () => keycloak.logout()
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
