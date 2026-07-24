export type IncidentStatusOption = {
  id: number;
  name: string;
  is_final: boolean;
};

// Fonte de verdade: seed de incident_status em db/migrations/0001_initial.sql.
// Hoje nao ha endpoint proprio pra listar status (decision_1 em next_steps.txt
// segue aberta); hardcode aqui e a opcao mais simples enquanto isso nao mudar.
export const INCIDENT_STATUSES: IncidentStatusOption[] = [
  { id: 1, name: "aberto", is_final: false },
  { id: 2, name: "equipe_acionada", is_final: false },
  { id: 3, name: "equipe_deslocada", is_final: false },
  { id: 4, name: "em_atendimento", is_final: false },
  { id: 5, name: "material_aguardando", is_final: false },
  { id: 6, name: "reparo_realizado", is_final: false },
  { id: 7, name: "em_validação", is_final: false },
  { id: 8, name: "concluído", is_final: true },
  { id: 9, name: "cancelado", is_final: true },
];

export function statusColor(statusName: string, isFinal: boolean): string {
  if (!isFinal) return "bg-cyan";
  if (statusName === "concluído") return "bg-success";
  return "bg-mid-gray"; // cancelado ou outro status final
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

// Monta a timeline na ordem pedida pelo usuario em s2_3 (ver current_state.txt
// /decisions_locked/frontend_public_pages_scope_s2_3): status atual primeiro,
// updates intermediarios em ordem decrescente de data, abertura por ultimo.
// Topo e fim mostram motivo+rota (alem de status+data); meio so status+data.
// A API ja retorna updates ordenado created_at desc, entao o primeiro item da
// lista E o status atual -- nao precisa duplicar, so separar do resto.
// Sem nenhuma atualizacao ainda, o incidente segue "aberto" desde a criacao:
// mostra so a entrada de abertura, evitando repetir a mesma informacao 2x.
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
