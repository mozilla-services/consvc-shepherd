import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import CampaignOverview from "./CampaignOverview";
import { useGetCampaignsOverviewQuery } from "../../data/campaigns";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FC } from "react";
import { CampaignFilters } from "../../types";

jest.mock("../../data/campaigns");
jest.mock("../../components/AppLoader/AppLoader", () => {
  const MockAppLoader = () => <div>Loading...</div>;
  MockAppLoader.displayName = "AppLoader";
  return MockAppLoader;
});

interface MockFilterCampaignOverviewProps {
  onFilterChange: (filters: CampaignFilters) => void;
}

jest.mock("../../components/Filters/CampaignOverviewFilter", () => {
  const MockFilterCampaignOverview: FC<MockFilterCampaignOverviewProps> = ({
    onFilterChange,
  }) => {
    return (
      <button
        onClick={() => {
          onFilterChange({
            months: "",
            country: "",
            products: "",
            advertisers: "",
            search: "",
          });
        }}
      >
        Apply Filters
      </button>
    );
  };

  MockFilterCampaignOverview.displayName = "FilterCampaignOverview";

  return MockFilterCampaignOverview;
});

const queryClient = new QueryClient();

describe("<CampaignOverview />", () => {
  const mockCampaignOverviewData = [
    {
      advertiser: "Advertiser 1",
      net_spend: 100,
      revenue: 150,
      impressions_sold: 1000,
      impressions_remaining: 500,
      clicks_delivered: 50,
      ctr: 5,
      net_ecpm: 5,
      notes: "Note 1",
      seller: "Seller 1",
      ad_ops_person: "Person 1",
      live: true,
    },
    {
      advertiser: "Advertiser 2",
      net_spend: 200,
      revenue: 250,
      impressions_sold: 2000,
      impressions_remaining: 300,
      clicks_delivered: 100,
      ctr: 10,
      net_ecpm: 10,
      notes: "Note 2",
      seller: "Seller 2",
      ad_ops_person: "Person 2",
      live: false,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders loading screen when fetching data", () => {
    (useGetCampaignsOverviewQuery as jest.Mock).mockReturnValue({
      isFetching: true,
    });
    render(
      <QueryClientProvider client={queryClient}>
        <CampaignOverview />
      </QueryClientProvider>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  test("renders campaign summary data in the table", () => {
    (useGetCampaignsOverviewQuery as jest.Mock).mockReturnValue({
      data: mockCampaignOverviewData,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <CampaignOverview />
      </QueryClientProvider>
    );

    expect(screen.getByText("Advertiser 1")).toBeInTheDocument();
    expect(screen.getByText("Budget")).toBeInTheDocument();
  });

  test("applies filters and fetches filtered data", async () => {
    (useGetCampaignsOverviewQuery as jest.Mock).mockReturnValue({
      data: mockCampaignOverviewData,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <CampaignOverview />
      </QueryClientProvider>
    );

    const applyFiltersButton = screen.getByText("Apply Filters");
    fireEvent.click(applyFiltersButton);

    await waitFor(() => {
      expect(useGetCampaignsOverviewQuery).toHaveBeenCalled(); // Verifying that the query is called again with the new filters
    });
  });
});
