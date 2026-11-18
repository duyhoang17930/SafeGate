"use client";

import { useMemo, useState } from "react";
import { HardHat, Plug, ScrollText, ShieldCheck, Users } from "lucide-react";

import { CameraCard, BuzzerCard, LcdCard, LedsCard, ServoCard } from "@/components/monitor/device-cards";
import { OUTCOME, OutcomePill, PhasePill, StatusPill, formatAgo, formatUptime } from "@/components/monitor/status";
import { ThemeSwitcher } from "@/components/theme-switcher";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { classify, type LogRow, type Outcome, type PiStatus, type User } from "@/lib/types";
import { useNow, usePoll } from "@/lib/usePoll";
import { cn } from "@/lib/utils";

const DEFAULT_PI_URL = process.env.NEXT_PUBLIC_PI_URL ?? "http://raspberrypi.local:8080";
const STORAGE_KEY = "pi-dashboard-url";
const OFFLINE_AFTER_MS = 3000;

function loadUrl(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT_PI_URL;
  } catch {
    return DEFAULT_PI_URL;
  }
}

function normalizeUrl(value: string): string {
  const trimmed = value.trim().replace(/\/+$/, "");
  if (!trimmed) return "";
  return /^https?:\/\//i.test(trimmed) ? trimmed : `http://${trimmed}`;
}

function PiUrlForm({ initial, onSubmit }: { initial: string; onSubmit: (url: string) => void }) {
  const [draft, setDraft] = useState(initial);
  return (
    <form
      className="flex w-full items-center gap-2 sm:w-auto"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit(normalizeUrl(draft));
      }}
    >
      <Input
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        placeholder="http://192.168.1.50:8080"
        aria-label="Raspberry Pi address"
        className="h-8 font-mono text-xs sm:w-64"
      />
      <Button type="submit" size="sm">
        <Plug />
        Connect
      </Button>
    </form>
  );
}

const KPI_COLOR: Record<Outcome, string> = {
  granted: "text-emerald-600",
  ppe_missing: "text-amber-600",
  denied: "text-red-600",
};

function KpiCard({ outcome, session, today }: { outcome: Outcome; session: number; today: number }) {
  const { label, icon: Icon } = OUTCOME[outcome];
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          {label}
          <Icon className={cn("h-4 w-4", KPI_COLOR[outcome])} />
        </div>
        <div className="text-3xl font-semibold">{session}</div>
        <div className="text-xs text-muted-foreground">
          since start · <span className={KPI_COLOR[outcome]}>{today} today</span>
        </div>
      </CardContent>
    </Card>
  );
}

function Check({ value, label }: { value: boolean | null; label: string }) {
  if (value === null) return <StatusPill tone="idle">{label}: -</StatusPill>;
  return <StatusPill tone={value ? "ok" : "bad"}>{label}: {value ? "Yes" : "No"}</StatusPill>;
}

export default function Dashboard() {
  const [piUrl, setPiUrl] = useState(loadUrl);
  const changeUrl = (url: string) => {
    setPiUrl(url);
    try {
      localStorage.setItem(STORAGE_KEY, url);
    } catch {
      /* storage unavailable: keep for this session only */
    }
  };

  const base = piUrl || null;
  const status = usePoll<PiStatus>(base && `${base}/api/status`, 500);
  const logs = usePoll<LogRow[]>(base && `${base}/api/logs?limit=100`, 3000);
  const users = usePoll<User[]>(base && `${base}/api/users`, 10000);
  const now = useNow(1000);
  const connected = status.lastOk !== null && now - status.lastOk < OFFLINE_AFTER_MS;

  // Reload the MJPEG stream each time the connection comes back.
  const [streamKey, setStreamKey] = useState(0);
  const [wasConnected, setWasConnected] = useState(connected);
  if (connected !== wasConnected) {
    setWasConnected(connected);
    if (connected) setStreamKey((key) => key + 1);
  }

  const s = status.data;
  const d = s?.devices;
  const event = s?.last_event ?? null;

  const today = useMemo(() => {
    const day = new Date().toISOString().slice(0, 10);
    const counts: Record<Outcome, number> = { granted: 0, ppe_missing: 0, denied: 0 };
    for (const row of logs.data ?? []) {
      if (row.timestamp.startsWith(day)) counts[classify(row.status, row.detail)] += 1;
    }
    return counts;
  }, [logs.data]);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="flex min-h-14 flex-wrap items-center justify-between gap-3 px-3 py-2 sm:px-4 lg:px-6">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <ShieldCheck className="h-5 w-5 shrink-0 text-sky-500" />
            <div className="min-w-0">
              <h1 className="truncate text-base font-semibold tracking-tight sm:text-lg">{s?.system.title ?? "Safety Access"} Monitor</h1>
              <p className="hidden truncate text-xs text-muted-foreground sm:block">
                Raspberry Pi face + PPE access control · camera, LCD, LEDs, servo and buzzer
              </p>
            </div>
          </div>
          <div className="flex w-full items-center gap-2 sm:w-auto">
            <PiUrlForm key={piUrl} initial={piUrl} onSubmit={changeUrl} />
            <ThemeSwitcher />
          </div>
        </div>
      </header>

      <main className="space-y-4 p-4 lg:px-6">
        <div className="flex flex-wrap items-center gap-2">
          {connected ? (
            <span className="rounded-full border border-emerald-500 px-3 py-1 text-xs font-medium text-emerald-600">● Connected</span>
          ) : (
            <span className="rounded-full border border-red-500 px-3 py-1 text-xs font-medium text-red-600">
              ● {status.lastOk ? "Connection lost" : "Connecting…"}
              {status.error && ` (${status.error})`}
            </span>
          )}
          {s && <PhasePill phase={s.system.phase} />}
          {s?.system.hardware_mock && <StatusPill tone="warn">GPIO mock mode</StatusPill>}
          {s && <span className="text-xs text-muted-foreground">Uptime {formatUptime(s.system.uptime_s)}</span>}
        </div>

        {!connected && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            {status.lastOk
              ? "Connection to the Raspberry Pi lost. Values below are the last ones received."
              : `Cannot reach ${piUrl || "the Raspberry Pi"}. Check the address and that main.py is running.`}
          </p>
        )}

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiCard outcome="granted" session={s?.counters.granted ?? 0} today={today.granted} />
          <KpiCard outcome="ppe_missing" session={s?.counters.ppe_missing ?? 0} today={today.ppe_missing} />
          <KpiCard outcome="denied" session={s?.counters.denied ?? 0} today={today.denied} />
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                Registered users
                <Users className="h-4 w-4 text-sky-500" />
              </div>
              <div className="text-3xl font-semibold">{users.data?.length ?? s?.system.users ?? "-"}</div>
              <div className="text-xs text-muted-foreground">face profiles in users.db</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid items-start gap-4 lg:grid-cols-3">
          <div className="flex flex-col gap-4 lg:col-span-2">
            <CameraCard
              camera={d?.camera}
              serverTime={s?.server_time}
              streamUrl={base ? `${base}/stream.mjpg?k=${streamKey}` : null}
            />
            <Card>
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 p-4 pb-3">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <HardHat className="h-4 w-4 text-sky-500" />
                  Last decision
                </CardTitle>
                {event && <OutcomePill outcome={classify(event.status, event.detail)} />}
              </CardHeader>
              <CardContent className="p-4 pt-0">
                {event ? (
                  <div className="space-y-2">
                    <div className="text-2xl font-semibold">{event.name}</div>
                    <div className="flex flex-wrap gap-1.5">
                      <Check value={event.helmet} label="Helmet" />
                      <Check value={event.vest} label="Vest" />
                      <StatusPill tone="info">Score {event.score.toFixed(2)}</StatusPill>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleTimeString()} · {event.detail || "-"}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No access attempts yet.</p>
                )}
              </CardContent>
            </Card>
          </div>
          <div className="flex flex-col gap-4">
            <LcdCard lcd={d?.lcd} />
            <LedsCard green={d?.green_led} yellow={d?.yellow_led} red={d?.red_led} />
            <ServoCard servo={d?.servo} />
            <BuzzerCard buzzer={d?.buzzer} />
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 p-4 pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <ScrollText className="h-4 w-4 text-sky-500" />
                Access log
              </CardTitle>
              <span className="text-xs text-muted-foreground">Latest {logs.data?.length ?? 0}</span>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="app-scrollbar max-h-96 overflow-auto rounded-lg border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Time</TableHead>
                      <TableHead>Result</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead className="text-right">Score</TableHead>
                      <TableHead>Detail</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(logs.data ?? []).map((row, i) => (
                      <TableRow key={`${row.timestamp}-${i}`}>
                        <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">{row.timestamp.replace("T", " ")}</TableCell>
                        <TableCell>
                          <OutcomePill outcome={classify(row.status, row.detail)} />
                        </TableCell>
                        <TableCell className="font-medium">{row.name}</TableCell>
                        <TableCell className="text-right font-mono text-xs">{Number(row.score).toFixed(2)}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{row.detail}</TableCell>
                      </TableRow>
                    ))}
                    {logs.data?.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                          No log entries yet.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 p-4 pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Users className="h-4 w-4 text-sky-500" />
                Registered users
              </CardTitle>
              <span className="text-xs text-muted-foreground">{users.data?.length ?? 0}</span>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="app-scrollbar max-h-96 overflow-auto rounded-lg border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Student ID</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(users.data ?? []).map((user) => (
                      <TableRow key={user.id}>
                        <TableCell className="font-medium">{user.name}</TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">{user.student_id}</TableCell>
                      </TableRow>
                    ))}
                    {users.data?.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={2} className="py-8 text-center text-muted-foreground">
                          None yet. Run <code className="font-mono">register_user.py</code> on the Pi.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>

        <p className="text-center text-xs text-muted-foreground">
          Polling {piUrl || "-"} · status every 0.5 s
          {status.lastOk && ` · last update ${formatAgo((now - status.lastOk) / 1000)}`}
        </p>
      </main>
    </div>
  );
}
