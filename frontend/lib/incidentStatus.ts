export type IncidentStatusOption = {
  id: number;
  name: string;
  is_final: boolean;
};

// Fonte de verdade: seed de incident_status em db/migrations/0001_initial.sql.
export const INCIDENT_STATUSES: IncidentStatusOption[] = [
  { id: 1, name: "Aberto", is_final: false },
  { id: 2, name: "Equipe acionada", is_final: false },
  { id: 3, name: "Equipe deslocada", is_final: false },
  { id: 4, name: "Em atendimento", is_final: false },
  { id: 5, name: "Aguardando", is_final: false },
  { id: 6, name: "Reparo realizado", is_final: false },
  { id: 7, name: "Em validação", is_final: false },
  { id: 8, name: "Concluído", is_final: true },
  { id: 9, name: "Cancelado", is_final: true },
];

export function statusColor(statusName: string, isFinal: boolean): string {
  if (!isFinal) return "bg-yellow";
  if (statusName === "concluído") return "bg-success";
  return "bg-red"; // cancelado ou outro status final
}

export type TimelineEntry = {
  status_name: string;
  is_final: boolean;
  date: string;
  comment?: string | null;
  type_name?: string;
  route_name?: string;
};

type TimelineIncident = {
  type_name: string;
  route_name: string;
  created_at: string;
};

type TimelineUpdate = {
  status_name: string;
  status_is_final: boolean;
  comment: string | null;
  created_at: string;
};

export function buildTimelineEntries(
  incident: TimelineIncident,
  updates: TimelineUpdate[],
): TimelineEntry[] {
  const abertura: TimelineEntry = {
    status_name: "aberto",
    is_final: false,
    date: incident.created_at,
    type_name: incident.type_name,
    route_name: incident.route_name,
  };

  if (updates.length === 0) {
    return [abertura];
  }

  const [atual, ...intermediarios] = updates;

  const topo: TimelineEntry = {
    status_name: atual.status_name,
    is_final: atual.status_is_final,
    date: atual.created_at,
    comment: atual.comment,
    type_name: incident.type_name,
    route_name: incident.route_name,
  };

  const meio: TimelineEntry[] = intermediarios.map((u) => ({
    status_name: u.status_name,
    is_final: u.status_is_final,
    date: u.created_at,
    comment: u.comment,
  }));

  return [topo, ...meio, abertura];
}
