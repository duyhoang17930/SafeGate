"use client";

import dynamic from "next/dynamic";

// The dashboard is live data from the Pi plus browser-only state (localStorage,
// clock), so it is rendered on the client only.
const Dashboard = dynamic(() => import("@/components/dashboard"), { ssr: false });

export default function Home() {
  return <Dashboard />;
}
