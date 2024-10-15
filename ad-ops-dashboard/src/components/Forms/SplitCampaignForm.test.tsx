import "@testing-library/jest-dom";

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { useSplitCampaignMutation } from "../../data/campaigns";
import SplitCampaignForm from "./SplitCampaignForm";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { splitCampaign } from "../../fixtures/campaignFixtures";

jest.mock("../../data/campaigns", () => ({
  useSplitCampaignMutation: jest.fn(),
}));

const queryClient = new QueryClient();

describe("SplitCampaignForm", () => {
  const mockHandleClose = jest.fn();
  const formData = splitCampaign;

  beforeEach(() => {
    jest.clearAllMocks();

    const mockMutateAsync = jest.fn().mockResolvedValue(true);
    (useSplitCampaignMutation as jest.Mock).mockReturnValue({
      mutateAsync: mockMutateAsync,
    });
  });

  test("populates the form fields with provided data", () => {
    render(
      <SplitCampaignForm formData={formData} handleClose={mockHandleClose} />
    );

    expect(screen.getByLabelText(/Ad Ops Person/i)).toHaveValue("John Doe");
    expect(screen.getByLabelText(/Seller/i)).toHaveValue("Some Seller");
    expect(screen.getByLabelText(/Start Date/i)).toHaveValue("2023-10-01");
    expect(screen.getByLabelText(/End Date/i)).toHaveValue("2023-10-31");
    expect(screen.getByLabelText(/Notes/i)).toHaveValue(
      "Initial campaign notes"
    );
    expect(screen.getByLabelText(/Kevel Flight Id/i)).toHaveValue(123);
    expect(screen.getByLabelText(/Impressions Sold/i)).toHaveValue(1000);
    expect(screen.getByLabelText(/Net spend/i)).toHaveValue(500);
  });

  test("appends a new campaign object when the add button is clicked", () => {
    render(
      <SplitCampaignForm formData={formData} handleClose={mockHandleClose} />
    );

    expect(screen.getAllByLabelText(/Ad Ops Person/i)).toHaveLength(1);
    fireEvent.click(screen.getByRole("button", { name: /Split Campaign/i }));
    expect(screen.getAllByLabelText(/Ad Ops Person/i)).toHaveLength(2);
  });

  test("submits the form successfully", async () => {
    const { mutateAsync } = useSplitCampaignMutation() as jest.Mock;

    render(
      <QueryClientProvider client={queryClient}>
        <SplitCampaignForm formData={formData} handleClose={mockHandleClose} />
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByLabelText(/Ad Ops Person/i), {
      target: { value: "Jane Smith" },
    });

    fireEvent.click(screen.getByRole("button", { name: /Save/i }));

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalled();
    });

    expect(mockHandleClose).toHaveBeenCalled();
  });
});
