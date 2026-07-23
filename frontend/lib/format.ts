export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatAddress(
  city: string | null,
  street: string | null,
  cep: string,
): string {
  const parts = [city, street].filter(Boolean);
  return parts.length > 0 ? `${parts.join(", ")} - ${cep}` : cep;
}
