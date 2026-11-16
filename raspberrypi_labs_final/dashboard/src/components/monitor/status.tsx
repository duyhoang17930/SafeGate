import { Ban, CheckCircle2, CircleDashed, HardHat, Loader2, ScanFace, UserX, Users, WifiOff, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import type { Outcome, Phase } from "@/lib/types";

export type Tone = "ok" | "warn" | "bad" | "info" | "idle";

// Same pill palette as EOS-SOFT's ServiceStatusBadge.
const TONE_CLASS: Record<Tone, string> = {
  ok: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  warn: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  bad: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300",
  info: "bg-sky-50 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  idle: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
};

export function StatusPill({
  tone,
  icon: Icon,
  children,
  className,
  spin,
}: {
  tone: Tone;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
  spin?: boolean;
}) {
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium", TONE_CLASS[tone], className)}>
      {Icon && <Icon className={cn("h-3 w-3", spin && "animate-spin")} />}
      {children}
    </span>
  );
}

export const OUTCOME: Record<Outcome, { label: string; tone: Tone; icon: LucideIcon }> = {
  granted: { label: "Granted", tone: "ok", icon: CheckCircle2 },
  ppe_missing: { label: "PPE missing", tone: "warn", icon: HardHat },
  denied: { label: "Denied", tone: "bad", icon: Ban },
};

export function OutcomePill({ outcome }: { outcome: Outcome }) {
  const { label, tone, icon } = OUTCOME[outcome];
  return (
    <StatusPill tone={tone} icon={icon}>
      {label}
    </StatusPill>
  );
}

export const PHASE: Record<Phase, { label: string; tone: Tone; icon: LucideIcon; spin?: boolean }> = {
  starting: { label: "Starting", tone: "idle", icon: Loader2, spin: true },
  waiting: { label: "Waiting for face", tone: "idle", icon: CircleDashed },
  scanning: { label: "Scanning", tone: "info", icon: ScanFace },
  granted: { label: "Access granted", tone: "ok", icon: CheckCircle2 },
  ppe_missing: { label: "PPE missing", tone: "warn", icon: HardHat },
  denied: { label: "Access denied", tone: "bad", icon: UserX },
  no_users: { label: "No users registered", tone: "warn", icon: Users },
};

export function PhasePill({ phase }: { phase: Phase }) {
  const info = PHASE[phase] ?? PHASE.starting;
  return (
    <StatusPill tone={info.tone} icon={info.icon} spin={info.spin}>
      {info.label}
    </StatusPill>
  );
}

export function OfflinePill() {
  return (
    <StatusPill tone="idle" icon={WifiOff}>
      Offline
    </StatusPill>
  );
}

export function formatUptime(seconds: number): string {
  const s = Math.floor(seconds);
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  return h > 0 ? `${h}h ${m}m` : m > 0 ? `${m}m ${s % 60}s` : `${s}s`;
}

export function formatAgo(seconds: number): string {
  if (seconds < 1) return "just now";
  if (seconds < 60) return `${Math.floor(seconds)}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}
