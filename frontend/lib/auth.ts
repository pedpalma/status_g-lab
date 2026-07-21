// Storage e leitura do JWT no navegador. Sem refresh token: quando o token
// expira (JWT_EXPIRE_MINUTES), o usuário precisa logar de novo.

const TOKEN_KEY = "glab_token";

export type JwtPayload = {
  sub: string;
  role: "tecnico" | "admin";
  exp: number;
};

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// Decodifica o payload apenas para leitura (role, exp). Não valida
// assinatura no frontend: quem valida de verdade é o backend, a cada
// request (get_current_user).
export function decodeToken(token: string): JwtPayload | null {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

export function isTokenValid(token: string | null): boolean {
  if (!token) return false;
  const payload = decodeToken(token);
  if (!payload) return false;
  return payload.exp * 1000 > Date.now();
}
