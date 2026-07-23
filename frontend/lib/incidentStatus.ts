export function statusColor(statusName: string, isFinal: boolean): string {
  if (!isFinal) return "bg-cyan";
  if (statusName === "concluído") return "bg-success";
  return "bg-mid-gray"; // cancelado ou outro status final
}
