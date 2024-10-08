import Dashboard from "./pages/Dashboard/Dashboard";
import CampaignOverview from "./pages/CampaignOverview/CampaignOverview";
import InventoryOverview from "./pages/InventoryOverview/InventoryOverview";
import Page404 from "./pages/Page404";
import Layout from "./components/Layout/AppLayout";

export const routes = [
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "campaign", element: <CampaignOverview /> },
      { path: "inventory", element: <InventoryOverview /> },
      { path: "*", element: <Page404 /> },
    ],
  },
];
