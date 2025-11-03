// import type { Statsig } from "@flags-sdk/statsig";
// import {
//   StatsigProvider,
//   useClientBootstrapInit,
// } from "@statsig/react-bindings";
// import { StatsigAutoCapturePlugin } from '@statsig/web-analytics';

  children: React.ReactNode;
  datafile: any;
}) {
  // if (!datafile) throw new Error("Missing datafile");

  // const client = useClientBootstrapInit(
  //   import.meta.env.VITE_STATSIG_CLIENT_KEY as string,
  //   datafile.user,
  //   JSON.stringify(datafile),
  //   { plugins: [ new StatsigAutoCapturePlugin() ] }
  // );

  // return (
  //   <StatsigProvider user={datafile.user} client={client} >
  //     {children}
  //   </StatsigProvider>
  // );
  return <>{children}</>;
}
