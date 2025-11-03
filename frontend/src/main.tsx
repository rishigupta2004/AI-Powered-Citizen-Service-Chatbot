

import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import MyStatsigProvider from "./MyStatsigProvider";

createRoot(document.getElementById("root")!).render(
  <MyStatsigProvider>
    <App />
  </MyStatsigProvider>
);
  