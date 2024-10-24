import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import FilterCampaignOverview from "./CampaignOverviewFilter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

const handleFilterChange = () => {
  // No-op for testing purposes
};

describe("<FilterCampaignOverview />", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders loading state while fetching data", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <FilterCampaignOverview onFilterChange={handleFilterChange} />
      </QueryClientProvider>
    );

    expect(screen.getByLabelText("Filter By Month")).toBeInTheDocument();
    expect(screen.getByLabelText("Filter By Countries")).toBeInTheDocument();
    expect(screen.getByLabelText("Filter By Products")).toBeInTheDocument();
    expect(screen.getByLabelText("Filter By Advertisers")).toBeInTheDocument();
    expect(screen.getByLabelText("Search")).toBeInTheDocument();
  });

  test("renders product, country, and advertiser options correctly", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <FilterCampaignOverview onFilterChange={handleFilterChange} />
      </QueryClientProvider>
    );

    expect(screen.getByLabelText("Filter By Products")).toBeInTheDocument();
    fireEvent.mouseDown(screen.getByLabelText("Filter By Products"));
    expect(
      screen.getByText("Open-source disintermediate flexibility")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Filter By Countries")).toBeInTheDocument();
    expect(screen.getByLabelText("Filter By Advertisers")).toBeInTheDocument();
  });

  test("calls onFilterChange with correct filters when values change", async () => {
    const onFilterChange = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <FilterCampaignOverview onFilterChange={onFilterChange} />
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByLabelText("Search"), {
      target: { value: "Test Search" },
    });

    await waitFor(() => {
      expect(onFilterChange).toHaveBeenCalledWith(
        expect.objectContaining({ search: "Test Search" })
      );
    });
  });

  test("debounces filter changes", async () => {
    jest.useFakeTimers();
    const onFilterChange = jest.fn();

    render(
      <QueryClientProvider client={queryClient}>
        <FilterCampaignOverview onFilterChange={onFilterChange} />
      </QueryClientProvider>
    );
    fireEvent.change(screen.getByLabelText("Search"), {
      target: { value: "First" },
    });
    fireEvent.change(screen.getByLabelText("Search"), {
      target: { value: "Second" },
    });

    jest.advanceTimersByTime(500);

    await waitFor(() => {
      expect(onFilterChange).toHaveBeenCalledTimes(1);
      expect(onFilterChange).toHaveBeenCalledWith(
        expect.objectContaining({ search: "Second" })
      );
    });
    jest.useRealTimers();
  });
});
