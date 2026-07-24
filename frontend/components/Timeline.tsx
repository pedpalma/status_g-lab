import { formatDateTime } from "../lib/format";
import { statusColor, type TimelineEntry } from "../lib/incidentStatus";

// Componente de apresentação puro (sem hooks), pra poder ser usado tanto pela
// página pública de detalhe (server component) quanto pela pagina privada
// (client component), sem duplicar o JSX da timeline nos 2 lugares.
export default function Timeline({ entries }: { entries: TimelineEntry[] }) {
  return (
    <ol className="flex flex-col gap-4 border-t border-navy-light pt-4">
      {entries.map((entry, i) => (
        <li key={i} className="flex flex-col gap-1 text-sm">
          <div className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${statusColor(entry.status_name, entry.is_final)}`}
            />
            <span className="text-off-white">{entry.status_name}</span>
            <span className="text-mid-gray">
              · {formatDateTime(entry.date)}
            </span>
          </div>
          {(entry.type_name || entry.route_name) && (
            <p className="pl-4 text-xs text-mid-gray">
              {entry.type_name} · {entry.route_name}
            </p>
          )}
          {entry.comment && (
            <p className="pl-4 text-xs text-light-gray">{entry.comment}</p>
          )}
        </li>
      ))}
    </ol>
  );
}
