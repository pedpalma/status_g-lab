"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { clearToken, decodeToken, getToken, isTokenValid, setToken } from "../../lib/auth";
import { login as loginRequest } from "../../lib/api";

type AuthState = {
  token: string | null;
  role: "tecnico" | "admin" | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Sincroniza o estado com o localStorage (fonte externa) uma única vez
    // no mount. É o padrão "mounted guard" (SSR não tem acesso a
    // localStorage), documentado pelo próprio Next.js. A regra nova do
    // eslint-plugin-react-hooks marca isso como erro por padrão; aqui é
    // um falso positivo conhecido, por isso o disable pontual.
    const stored = getToken();
    if (isTokenValid(stored)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setTokenState(stored);
    } else {
      clearToken();
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsLoading(false);
  }, []);

  const role = token ? decodeToken(token)?.role ?? null : null;

  async function login(email: string, password: string) {
    const { access_token } = await loginRequest(email, password);
    setToken(access_token);
    setTokenState(access_token);
  }

  function logout() {
    clearToken();
    setTokenState(null);
  }

  return (
    <AuthContext.Provider value={{ token, role, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro de AuthProvider");
  return ctx;
}
