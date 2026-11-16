"use client";

import { useEffect, useState } from "react";

export interface PollResult<T> {
  data: T | null;
  error: string | null;
  /** Epoch ms of the last successful response. */
  lastOk: number | null;
}

const EMPTY: PollResult<never> = { data: null, error: null, lastOk: null };

/** Polls a JSON endpoint every `intervalMs`, never overlapping requests. */
export function usePoll<T>(url: string | null, intervalMs: number): PollResult<T> {
  // Results are tagged with their URL so switching URL never shows stale data.
  const [state, setState] = useState<PollResult<T> & { url: string | null }>({ ...EMPTY, url: null });

  useEffect(() => {
    if (!url) return;
    const setResult = (update: (previous: PollResult<T>) => PollResult<T>) =>
      setState((previous) => ({ ...update(previous.url === url ? previous : EMPTY), url }));

    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let controller: AbortController | undefined;

    const tick = async () => {
      controller = new AbortController();
      const timeout = setTimeout(() => controller?.abort(), Math.max(2000, intervalMs * 2));
      try {
        const response = await fetch(url, { cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = (await response.json()) as T;
        if (!stopped) setResult(() => ({ data, error: null, lastOk: Date.now() }));
      } catch (error) {
        if (!stopped) {
          const message = error instanceof Error ? error.message : String(error);
          setResult((previous) => ({ ...previous, error: message }));
        }
      } finally {
        clearTimeout(timeout);
        if (!stopped) timer = setTimeout(tick, intervalMs);
      }
    };

    tick();
    return () => {
      stopped = true;
      clearTimeout(timer);
      controller?.abort();
    };
  }, [url, intervalMs]);

  return url && state.url === url ? state : EMPTY;
}

/** Re-renders every `intervalMs` so "x seconds ago" labels stay fresh. */
export function useNow(intervalMs = 1000): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}
