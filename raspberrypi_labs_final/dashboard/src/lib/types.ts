export type Phase =
  | "starting"
  | "waiting"
  | "scanning"
  | "granted"
  | "ppe_missing"
  | "denied"
  | "no_users";

export interface PinDevice {
  on: boolean;
  pin: number;
}

export interface ServoDevice {
  angle: number;
  pin: number;
  door: "open" | "locked";
}

export interface LcdDevice {
  connected: boolean;
  address: string;
  cols: number;
  rows: number;
  lines: string[];
}

export interface CameraDevice {
  online: boolean;
  width: number;
  height: number;
  last_frame_at: number | null;
}

export interface AccessEvent {
  timestamp: string;
  status: string;
  name: string;
  score: number;
  detail: string;
  helmet: boolean | null;
  vest: boolean | null;
}

export interface PiStatus {
  server_time: number;
  system: {
    title: string;
    phase: Phase;
    started_at: number;
    uptime_s: number;
    hardware_mock: boolean;
    users: number;
  };
  devices: {
    green_led: PinDevice;
    yellow_led: PinDevice;
    red_led: PinDevice;
    buzzer: PinDevice;
    servo: ServoDevice;
    lcd: LcdDevice;
    camera: CameraDevice;
  };
  last_event: AccessEvent | null;
  counters: { granted: number; ppe_missing: number; denied: number };
}

/** One row of logs/access.csv (all values are strings). */
export interface LogRow {
  timestamp: string;
  status: string;
  name: string;
  score: string;
  detail: string;
}

export interface User {
  id: number;
  student_id: string;
  name: string;
  created_at: string;
}

export type Outcome = "granted" | "ppe_missing" | "denied";

export function classify(status: string, detail = ""): Outcome {
  if (status === "GRANTED") return "granted";
  // Older logs recorded missing PPE as DENIED with a MISSING_* detail.
  if (status === "PPE_MISSING" || detail.startsWith("MISSING_")) return "ppe_missing";
  return "denied";
}
