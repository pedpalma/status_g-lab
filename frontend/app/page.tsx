// Força renderização dinâmica: está página verifica o status do backend a
// cada requisição. Sem isso, o Next.js poderia pré-renderizar a página
// como estática em build de produção e congelar o status verificado no
// momento do build.
export const dynamic = "force-dynamic";

type BackendStatus = {
  ok: boolean;
};

async function getBackendStatus(): Promise<BackendStatus> {
  const baseUrl = process.env.BACKEND_INTERNAL_URL;

  if (!baseUrl) {
    return { ok: false };
  }

  try {
    const res = await fetch(`${baseUrl}/health`, { cache: "no-store" });
    return { ok: res.ok };
  } catch {
    return { ok: false };
  }
}

export default async function Home() {
  const backend = await getBackendStatus();

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-8 px-6 py-24">
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">
          Status G-Lab Telecom
        </h1>
        <p className="max-w-sm text-sm text-zinc-500">
          Scaffold de infraestrutura. Nenhuma funcionalidade de negocio foi
          implementada ainda.
        </p>
      </div>

      <div className="flex w-full max-w-sm flex-col gap-3 rounded-lg border border-zinc-200 p-4 text-sm dark:border-zinc-800">
        <div className="flex items-center justify-between">
          <span className="text-zinc-500">frontend</span>
          <StatusBadge ok label="rodando" />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-zinc-500">backend</span>
          <StatusBadge
            ok={backend.ok}
            label={backend.ok ? "conectado" : "indisponível"}
          />
        </div>
      </div>
    </main>
  );
}

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className="flex items-center gap-2">
      <span
        className={`h-2 w-2 rounded-full ${ok ? "bg-green-500" : "bg-red-500"}`}
      />
      {label}
    </span>
  );
}
