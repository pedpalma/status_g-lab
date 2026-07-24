export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";
import PublicHeader from "../../../components/public/PublicHeader";
import Timeline from "../../../components/Timeline";
import { formatAddress, formatDateTime } from "../../../lib/format";
import { statusColor, buildTimelineEntries } from "../../../lib/incidentStatus";

type Incident = {
  id: number;
  type_name: string;
  route_name: string;
  status_name: string;
  status_is_final: boolean;
  cep: string;
  city: string | null;
  street: string | null;
  description: string;
  created_at: string;
  closed_at: string | null;
};

type IncidentUpdate = {
  status_name: string;
  status_is_final: boolean;
  comment: string | null;
  created_at: string;
};

async function getIncident(id: string): Promise<Incident | null> {
  const baseUrl = process.env.BACKEND_INTERNAL_URL;
  if (!baseUrl) return null;

  try {
    const res = await fetch(`${baseUrl}/incidents/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getUpdates(id: string): Promise<IncidentUpdate[]> {
  const baseUrl = process.env.BACKEND_INTERNAL_URL;
  if (!baseUrl) return [];

  try {
    const res = await fetch(`${baseUrl}/incidents/${id}/updates`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function IncidentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const incident = await getIncident(id);

  if (!incident) notFound();

  const updates = await getUpdates(id);
  const timeline = buildTimelineEntries(incident, updates);

  return (
    <>
      <PublicHeader />
      <main className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-10">
        <Link href="/" className="text-sm text-cyan hover:underline">
          ← Voltar para incidentes
        </Link>

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
            {incident.closed_at
              ? ` · Encerrado em ${formatDateTime(incident.closed_at)}`
              : ""}
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
          <h2 className="font-display text-sm font-semibold text-off-white">
            Histórico
          </h2>
          <Timeline entries={timeline} />
        </div>
      </main>
    </>
  );
}
