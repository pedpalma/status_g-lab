"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  incidentsApi,
  incidentUpdatesApi,
  ApiError,
  type Incident,
  type IncidentUpdate,
} from "../../../../lib/api";
import { formatAddress, formatDateTime } from "../../../../lib/format";
import { statusColor, buildTimelineEntries, INCIDENT_STATUSES } from "../../../../lib/incidentStatus";
import Timeline from "../../../../components/Timeline";

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  const incidentId = Number(params.id);

  const [incident, setIncident] = useState<Incident | null>(null);
  const [updates, setUpdates] = useState<IncidentUpdate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ status_id: "", comment: "" });
  const [isSaving, setIsSaving] = useState(false);

  async function loadData() {
    setIsLoading(true);
    try {
      const [incidentRes, updatesRes] = await Promise.all([
        incidentsApi.get(incidentId),
        incidentUpdatesApi.list(incidentId),
      ]);
      setIncident(incidentRes);
      setUpdates(updatesRes);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao carregar incidente.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    // loadData só depende de incidentId, que já está no array de deps; a
    // função em si é redefinida a cada render (mesmo padrão de
    // loadUsers/loadRoutes nas telas admin), então incluir loadData aqui
    // causaria loop. Mesmo racional de frontend_eslint_set_state_in_effect
    // em current_state.txt, agora pra exhaustive-deps.
    // eslint-disable-next-line react-hooks/set-state-in-effect, react-hooks/exhaustive-deps
    loadData();
  }, [incidentId]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSaving(true);
    try {
      await incidentUpdatesApi.create(incidentId, {
        status_id: Number(form.status_id),
        comment: form.comment || undefined,
      });
      setForm({ status_id: "", comment: "" });
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao registrar atualização.");
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return <p className="text-sm text-mid-gray">Carregando...</p>;
  }

  if (!incident) {
    return <p className="text-sm text-red-400">{error || "Incidente não encontrado."}</p>;
  }

  const timeline = buildTimelineEntries(incident, updates);

  return (
    <div className="flex flex-col gap-6">
      <Link href="/painel/incidents" className="text-sm text-cyan hover:underline">
        ← Voltar para incidentes
      </Link>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${statusColor(incident.status_name, incident.status_is_final)}`}
          />
          <span className="font-display text-lg font-semibold text-off-white">
            {incident.status_name}
          </span>
        </div>
        <p className="text-sm text-mid-gray">
          Aberto em {formatDateTime(incident.created_at)}
          {incident.closed_at ? ` · Encerrado em ${formatDateTime(incident.closed_at)}` : ""}
        </p>
      </div>

      <dl className="flex flex-col gap-3 border-t border-navy-light pt-4 text-sm">
        <div>
          <dt className="text-mid-gray">Motivo</dt>
          <dd className="text-off-white">{incident.type_name}</dd>
        </div>
        <div>
          <dt className="text-mid-gray">Rota</dt>
          <dd className="text-off-white">{incident.route_name}</dd>
        </div>
        <div>
          <dt className="text-mid-gray">Endereço</dt>
          <dd className="text-off-white">
            {formatAddress(incident.city, incident.street, incident.cep)}
          </dd>
        </div>
        <div>
          <dt className="text-mid-gray">Descrição</dt>
          <dd className="text-off-white">{incident.description}</dd>
        </div>
      </dl>

      <div>
        <h2 className="font-display text-sm font-semibold text-off-white">Histórico</h2>
        <Timeline entries={timeline} />
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4 border-t border-navy-light pt-6">
        <h2 className="font-display text-sm font-semibold text-off-white">Nova atualização</h2>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-mid-gray">Status</label>
          <select
            required
            value={form.status_id}
            onChange={(e) => setForm({ ...form, status_id: e.target.value })}
            className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
          >
            <option value="">Selecione...</option>
            {INCIDENT_STATUSES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-mid-gray">Comentário (opcional)</label>
          <textarea
            rows={3}
            value={form.comment}
            onChange={(e) => setForm({ ...form, comment: e.target.value })}
            className="rounded-md border border-navy-light bg-navy-light px-3 py-2 text-sm text-white outline-none focus:border-cyan"
          />
        </div>
        <div>
          <button
            type="submit"
            disabled={isSaving}
            className="rounded-md bg-blue-mid px-4 py-2 font-display text-sm font-medium text-white hover:bg-blue disabled:opacity-50"
          >
            {isSaving ? "Salvando..." : "Registrar atualização"}
          </button>
        </div>
      </form>
    </div>
  );
}
