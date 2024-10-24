import Dashboard from "./pages/Dashboard/Dashboard";
import Campaign from "./pages/Campaign/Campaign";
import CampaignOverview from "./pages/CampaignOverview/CampaignOverview";
import Page404 from "./pages/Page404";
import Layout from "./components/Layout/AppLayout";
import Debug from "./pages/Debug/Debug";
import { DefaultError } from "./components/Errors/DefaultError";

export const routes = [
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "campaign", element: <Campaign /> },
      { path: "campaign-overview", element: <CampaignOverview /> },
      { path: "*", element: <Page404 /> },
      { path: "debug", element: <Debug />, errorElement: <DefaultError /> }
    ],
  },
];
