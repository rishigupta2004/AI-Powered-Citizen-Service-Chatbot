

import React from "react";
import { StatsigProvider, useClientAsyncInit } from "@statsig/react-bindings";
import { StatsigAutoCapturePlugin } from "@statsig/web-analytics";
import { StatsigSessionReplayPlugin } from "@statsig/session-replay";

export default function MyStatsigProvider({ children }: { children: React.ReactNode }) {
  const { client } = useClientAsyncInit(
    import.meta.env.NEXT_PUBLIC_STATSIG_CLIENT_KEY!,
    { userID: "a-user" },
    { plugins: [new StatsigAutoCapturePlugin(), new StatsigSessionReplayPlugin()] }
  );

  return (
    <StatsigProvider client={client} loadingComponent={<div>Loading...</div>}>
      {children}
    </StatsigProvider>
  );
}
