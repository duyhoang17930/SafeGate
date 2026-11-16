import { Camera, DoorClosed, DoorOpen, Lightbulb, Monitor, Volume2, VolumeX } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { CameraDevice, LcdDevice, PinDevice, ServoDevice } from "@/lib/types";

import { StatusPill, formatAgo } from "./status";

function DeviceCard({
  title,
  icon: Icon,
  status,
  children,
  className,
}: {
  title: string;
  icon: typeof Camera;
  status?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 p-4 pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Icon className="h-4 w-4 text-sky-500" />
          {title}
        </CardTitle>
        {status}
      </CardHeader>
      <CardContent className="p-4 pt-0">{children}</CardContent>
    </Card>
  );
}

const LED_COLOR = {
  green: { on: "bg-emerald-500 shadow-[0_0_18px_4px_rgba(16,185,129,0.55)]", off: "bg-emerald-100 dark:bg-emerald-950" },
  yellow: { on: "bg-amber-400 shadow-[0_0_18px_4px_rgba(251,191,36,0.6)]", off: "bg-amber-100 dark:bg-amber-950" },
  red: { on: "bg-red-500 shadow-[0_0_18px_4px_rgba(239,68,68,0.55)]", off: "bg-red-100 dark:bg-red-950" },
} as const;

function LedRow({ color, label, meaning, device }: { color: keyof typeof LED_COLOR; label: string; meaning: string; device?: PinDevice }) {
  const on = device?.on ?? false;
  return (
    <div className="flex items-center gap-3 rounded-lg border px-3 py-2">
      <span
        className={cn("h-6 w-6 shrink-0 rounded-full border border-black/10 transition-all duration-150", on ? LED_COLOR[color].on : LED_COLOR[color].off)}
        aria-label={`${label} LED ${on ? "on" : "off"}`}
      />
      <div className="min-w-0 flex-1">
        <div className="text-sm font-medium">{label}</div>
        <div className="text-xs text-muted-foreground">
          {meaning} · GPIO {device?.pin ?? "-"}
        </div>
      </div>
      <span className={cn("font-mono text-xs font-semibold", on ? "text-foreground" : "text-muted-foreground")}>{on ? "ON" : "OFF"}</span>
    </div>
  );
}

export function LedsCard({ green, yellow, red }: { green?: PinDevice; yellow?: PinDevice; red?: PinDevice }) {
  const active = [green, yellow, red].filter((led) => led?.on).length;
  return (
    <DeviceCard
      title="Status LEDs"
      icon={Lightbulb}
      status={<StatusPill tone={active ? "info" : "idle"}>{active ? `${active} on` : "All off"}</StatusPill>}
    >
      <div className="space-y-2">
        <LedRow color="green" label="Green" meaning="Access granted" device={green} />
        <LedRow color="yellow" label="Yellow" meaning="PPE missing" device={yellow} />
        <LedRow color="red" label="Red" meaning="Access denied" device={red} />
      </div>
    </DeviceCard>
  );
}

export function BuzzerCard({ buzzer }: { buzzer?: PinDevice }) {
  const on = buzzer?.on ?? false;
  const Icon = on ? Volume2 : VolumeX;
  return (
    <DeviceCard
      title="Buzzer"
      icon={Volume2}
      status={<StatusPill tone={on ? "bad" : "idle"}>{on ? "Sounding" : "Silent"}</StatusPill>}
    >
      <div className="flex items-center gap-4 py-2">
        <div className="relative grid h-16 w-16 shrink-0 place-items-center">
          {on && <span className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-60" />}
          <div
            className={cn(
              "relative grid h-14 w-14 place-items-center rounded-full border",
              on ? "border-red-300 bg-red-50 text-red-600 dark:border-red-800 dark:bg-red-950 dark:text-red-300" : "bg-muted text-muted-foreground",
            )}
          >
            <Icon className="h-6 w-6" />
          </div>
        </div>
        <div>
          <div className="text-3xl font-semibold">{on ? "ON" : "OFF"}</div>
          <div className="text-xs text-muted-foreground">Active buzzer · GPIO {buzzer?.pin ?? "-"}</div>
        </div>
      </div>
    </DeviceCard>
  );
}

export function ServoCard({ servo }: { servo?: ServoDevice }) {
  const angle = servo?.angle ?? 0;
  const open = servo?.door === "open";
  return (
    <DeviceCard
      title="Door servo"
      icon={open ? DoorOpen : DoorClosed}
      status={
        <StatusPill tone={open ? "ok" : "idle"} icon={open ? DoorOpen : DoorClosed}>
          {open ? "Open" : "Locked"}
        </StatusPill>
      }
    >
      <svg viewBox="0 0 200 112" className="mx-auto w-full max-w-[200px]" role="img" aria-label={`Servo at ${angle} degrees`}>
        <path d="M20 100 A80 80 0 0 1 180 100" fill="none" className="stroke-muted" strokeWidth="10" strokeLinecap="round" />
        <path
          d="M20 100 A80 80 0 0 1 100 20"
          fill="none"
          className={open ? "stroke-emerald-500" : "stroke-slate-300 dark:stroke-slate-600"}
          strokeWidth="10"
          strokeLinecap="round"
        />
        <g style={{ transform: `rotate(${angle}deg)`, transformOrigin: "100px 100px", transition: "transform 0.6s ease" }}>
          <line x1="100" y1="100" x2="34" y2="100" className="stroke-foreground" strokeWidth="4" strokeLinecap="round" />
        </g>
        <circle cx="100" cy="100" r="6" className="fill-foreground" />
        <text x="12" y="111" fontSize="10" className="fill-muted-foreground">0°</text>
        <text x="91" y="11" fontSize="10" className="fill-muted-foreground">90°</text>
        <text x="170" y="111" fontSize="10" className="fill-muted-foreground">180°</text>
      </svg>
      <div className="mt-1 text-center">
        <span className="text-2xl font-semibold">{angle}°</span>
        <span className="text-xs text-muted-foreground"> · GPIO {servo?.pin ?? "-"}</span>
      </div>
    </DeviceCard>
  );
}

export function LcdCard({ lcd }: { lcd?: LcdDevice }) {
  const cols = lcd?.cols ?? 16;
  const rows = lcd?.rows ?? 2;
  const lines = Array.from({ length: rows }, (_, i) => (lcd?.lines[i] ?? "").slice(0, cols).padEnd(cols, " "));
  return (
    <DeviceCard
      title={`LCD ${cols}×${rows}`}
      icon={Monitor}
      status={
        <StatusPill tone={lcd?.connected ? "ok" : "warn"}>{lcd?.connected ? `I2C ${lcd.address}` : "Console fallback"}</StatusPill>
      }
    >
      <div className="app-scrollbar overflow-x-auto rounded-lg border-4 border-slate-800 bg-[#1f3fbf] p-2.5">
        <div className="mx-auto w-max">
          {lines.map((line, r) => (
            <div key={r} className="flex">
              {line.split("").map((ch, c) => (
                <span
                  key={c}
                  className="m-px grid h-7 w-[1.1rem] place-items-center bg-white/5 font-mono text-base leading-none text-[#e6f0ff] [text-shadow:0_0_4px_rgba(220,235,255,0.7)]"
                >
                  {ch}
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>
    </DeviceCard>
  );
}

export function CameraCard({
  camera,
  streamUrl,
  serverTime,
  className,
}: {
  camera?: CameraDevice;
  streamUrl: string | null;
  serverTime?: number;
  className?: string;
}) {
  const age = camera?.last_frame_at && serverTime ? serverTime - camera.last_frame_at : null;
  const live = (camera?.online ?? false) && age !== null && age < 5;
  return (
    <DeviceCard
      title="Camera"
      icon={Camera}
      className={className}
      status={
        live ? (
          <StatusPill tone="bad">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-rose-500" />
            </span>
            Live
          </StatusPill>
        ) : (
          <StatusPill tone="idle">Offline</StatusPill>
        )
      }
    >
      <div className="relative aspect-[4/3] w-full overflow-hidden rounded-lg border bg-muted/40">
        {streamUrl ? (
          // MJPEG streams need a plain <img>; next/image cannot render them.
          // eslint-disable-next-line @next/next/no-img-element
          <img src={streamUrl} alt="Live camera stream from the Raspberry Pi" className="h-full w-full object-contain" />
        ) : (
          <div className="grid h-full place-items-center text-sm text-muted-foreground">No stream</div>
        )}
      </div>
      <div className="mt-2 flex flex-wrap justify-between gap-2 text-xs text-muted-foreground">
        <span>
          {camera?.width ?? "-"}×{camera?.height ?? "-"} · USB / V4L2
        </span>
        <span>Last frame: {age === null ? "never" : formatAgo(age)}</span>
      </div>
    </DeviceCard>
  );
}
