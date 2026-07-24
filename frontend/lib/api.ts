// Fetch centralizado. Nenhum componente deve chamar fetch diretamente
// (ver conventions.md).

import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d: { msg: string }) => d.msg).join(", ")
      : detail || "Erro inesperado. Tente novamente.";
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// auth
export function login(email: string, password: string) {
  return request<{ access_token: string; token_type: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

// users
export type Role = "tecnico" | "admin";

export type User = {
  id: number;
  name: string;
  email: string;
  role: Role;
  is_active: boolean;
};

export type UserInput = {
  name: string;
  email: string;
  password: string;
  role: Role;
};

export type UserPatch = {
  name?: string;
  email?: string;
  role?: Role;
  is_active?: boolean;
};

export const usersApi = {
  list: () => request<User[]>("/users"),
  create: (data: UserInput) =>
    request<User>("/users", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: UserPatch) =>
    request<User>(`/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deactivate: (id: number) =>
    request<void>(`/users/${id}`, { method: "DELETE" }),
};

// routes (rotas de rede)
export type NetworkRoute = {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
};

export type NetworkRouteInput = { name: string; description?: string };
export type NetworkRoutePatch = Partial<NetworkRouteInput> & {
  is_active?: boolean;
};

export const routesApi = {
  list: () => request<NetworkRoute[]>("/routes"),
  create: (data: NetworkRouteInput) =>
    request<NetworkRoute>("/routes", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: NetworkRoutePatch) =>
    request<NetworkRoute>(`/routes/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deactivate: (id: number) =>
    request<void>(`/routes/${id}`, { method: "DELETE" }),
};

// incident types
export type IncidentType = {
  id: number;
  name: string;
  is_active: boolean;
};

export type IncidentTypeInput = { name: string };
export type IncidentTypePatch = Partial<IncidentTypeInput> & {
  is_active?: boolean;
};

export const incidentTypesApi = {
  list: () => request<IncidentType[]>("/incident-types"),
  create: (data: IncidentTypeInput) =>
    request<IncidentType>("/incident-types", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: IncidentTypePatch) =>
    request<IncidentType>(`/incident-types/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deactivate: (id: number) =>
    request<void>(`/incident-types/${id}`, { method: "DELETE" }),
};

// incidents
export type Incident = {
  id: number;
  type_id: number;
  type_name: string;
  route_id: number;
  route_name: string;
  status_id: number;
  status_name: string;
  status_is_final: boolean;
  cep: string;
  city: string | null;
  street: string | null;
  description: string;
  created_by: number;
  created_at: string;
  closed_at: string | null;
};

export type IncidentInput = {
  type_id: number;
  route_id: number;
  cep: string;
  description: string;
};

export const incidentsApi = {
  list: (params?: { status_id?: number; type_id?: number }) => {
    const query = new URLSearchParams();
    if (params?.status_id !== undefined)
      query.set("status_id", String(params.status_id));
    if (params?.type_id !== undefined)
      query.set("type_id", String(params.type_id));
    const qs = query.toString();
    return request<Incident[]>(`/incidents${qs ? `?${qs}` : ""}`);
  },
  get: (id: number) => request<Incident>(`/incidents/${id}`),
  create: (data: IncidentInput) =>
    request<Incident>("/incidents", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// incident updates (timeline)
export type IncidentUpdate = {
  id: number;
  incident_id: number;
  status_id: number;
  status_name: string;
  status_is_final: boolean;
  comment: string | null;
  created_by: number;
  created_at: string;
};

export type IncidentUpdateInput = {
  status_id: number;
  comment?: string;
};

export const incidentUpdatesApi = {
  list: (incidentId: number) =>
    request<IncidentUpdate[]>(`/incidents/${incidentId}/updates`),
  create: (incidentId: number, data: IncidentUpdateInput) =>
    request<IncidentUpdate>(`/incidents/${incidentId}/updates`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
