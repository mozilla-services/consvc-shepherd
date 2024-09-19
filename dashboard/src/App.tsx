import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { routes } from "./routes.tsx";
import { Suspense } from "react";
import AppLoader from "./components/AppLoader/AppLoader.tsx";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes);
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastContainer />

      <Suspense fallback={<AppLoader />}>
        <RouterProvider router={router} />
      </Suspense>
    </QueryClientProvider>
  );
}
