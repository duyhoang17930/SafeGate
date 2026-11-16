# Safety Access Monitor (dashboard)

Next.js + React + TypeScript dashboard for the Raspberry Pi safety access system.
UI uses the same shadcn/ui (new-york, neutral) components, lucide icons and
light/dark theme as EOS-SOFT.

It shows, live:

- Camera stream (MJPEG) and camera health
- LCD 16x2 contents, as currently shown on the real display
- Green / yellow / red LEDs, buzzer and door servo angle
- Current phase, last decision (name, score, helmet, vest)
- Granted / PPE missing / denied counters, access log, registered users

## Run

1. On the Pi, start the system: `python main.py` (serves the API on port 8080).
2. On any machine on the same network:

```bash
cd dashboard
npm install
npm run dev        # http://localhost:3000
```

Enter the Pi address in the header (for example `http://192.168.1.50:8080`);
it is remembered in the browser. A default can be set with
`NEXT_PUBLIC_PI_URL` in `.env.local` (see `.env.example`).

## Pi API used

| Endpoint            | Poll  | Content                                  |
|---------------------|-------|------------------------------------------|
| `/api/status`       | 0.5 s | devices, phase, last event, counters     |
| `/api/logs?limit=N` | 3 s   | latest rows of `logs/access.csv`         |
| `/api/users`        | 10 s  | registered users (no face embeddings)    |
| `/stream.mjpg`      | live  | camera stream                            |
