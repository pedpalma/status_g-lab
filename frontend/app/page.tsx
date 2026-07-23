// Página pública: lista de incidentes ativos e encerrados.
export const dynamic = "force-dynamic";

import Link from "next/link";
import PublicHeader from "../components/public/PublicHeader";
import { formatAddress, formatDateTime } from "../lib/format";
import { statusColor } from "../lib/incidentStatus";

type Incident = {
  id: number;
  type_name: string;
  route_name: string;
  status_name: string;
  status_is_final: boolean;
  cep: string;
  city: string | null;
  street: string | null;
  created_at: string;
  closed_at: string | null;
};

async function getIncidents(): Promise<Incident[]> {
  const baseUrl = process.env.BACKEND_INTERNAL_URL;
  if (!baseUrl) return [];

  try {
    const res = await fetch(`${baseUrl}/incidents`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function Home() {
  const incidents = await getIncidents();
  const ativos = incidents.filter((i) => !i.status_is_final);
  const encerrados = incidents.filter((i) => i.status_is_final);

  return (
    <>
      <PublicHeader />
      <main className="mx-auto flex max-w-3xl flex-col gap-10 px-6 py-10">
        <div>
          <h1 className="font-display text-xl font-semibold text-off-white">
            Incidentes da Rede
          </h1>
          <p className="mt-1 text-sm text-mid-gray">
            Acompanhamento de rompimentos, manutenções e demais ocorrências.
          </p>
        </div>

        <IncidentSection
          title="Ativos"
          incidents={ativos}
          emptyLabel="Nenhum incidente ativo no momento."
        />
        <IncidentSection
          title="Histórico"
          incidents={encerrados}
          emptyLabel="Nenhum incidente encerrado ainda."
        />
      </main>
    </>
  );
}

function IncidentSection({
  title,
  incidents,
  emptyLabel,
}: {
  title: string;
  incidents: Incident[];
  emptyLabel: string;
}) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-mid-gray">
        {title}
      </h2>
      {incidents.length === 0 ? (
        <p className="text-sm text-mid-gray">{emptyLabel}</p>
      ) : (
        <ul className="flex flex-col divide-y divide-navy-light border-t border-b border-navy-light">
          {incidents.map((incident) => (
            <li key={incident.id}>
              <Link
                href={`/incidents/${incident.id}`}
                className="flex flex-col gap-1 py-4 transition-colors hover:bg-navy-light/40"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${statusColor(incident.status_name, incident.status_is_final)}`}
                  />
                  <span className="text-sm font-medium text-off-white">
                    {incident.status_name}
                  </span>
                  <span className="text-xs text-mid-gray">
                    {formatDateTime(incident.created_at)}
                    {incident.closed_at
                      ? ` · encerrado em ${formatDateTime(incident.closed_at)}`
                      : ""}
                  </span>
                </div>
                <p className="text-sm text-off-white">{incident.type_name}</p>
                <p className="text-xs text-mid-gray">
                  {formatAddress(incident.city, incident.street, incident.cep)}{" "}
                  · {incident.route_name}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
