import Link from "next/link";

export default function PublicHeader() {
  return (
    <header className="flex h-(--topbar-h) items-center border-b border-navy-light bg-navy px-6">
      <Link
        href="/"
        className="font-display text-sm font-semibold tracking-tight text-off-white"
      >
        Status G-Lab Telecom
      </Link>
    </header>
  );
}
