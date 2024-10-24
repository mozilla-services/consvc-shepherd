import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import CampaignForm from "./CampaignForm";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCreateCampaignMutation } from "../../data/campaigns";
import { defaultCampaign, newCampaign } from "../../fixtures/campaignFixtures";

jest.mock("../../data/campaigns", () => ({
  useCreateCampaignMutation: jest.fn(),
  useUpdateCampaignMutation: jest.fn(),
}));

const mockCreateCampaign = jest.fn();

const setup = (props) => {
  render(
    <QueryClientProvider client={queryClient}>
      <CampaignForm {...props} />
    </QueryClientProvider>
  );
};
const queryClient = new QueryClient();

describe("<CampaignForm />", () => {
  const defaultProps = {
    formData: defaultCampaign,
    isUpdate: false,
    handleClose: jest.fn(),
    campaigns: [],
  };

  test("populates the form with initial values for updating a campaign", () => {
    const formData = newCampaign;
    setup({ ...defaultProps, formData, isUpdate: false });

    expect(screen.getByLabelText(/ad ops person/i)).toHaveValue("John Doe");
    expect(screen.getByLabelText(/impressions sold/i)).toHaveValue(1000);
    expect(screen.getByLabelText(/net spend/i)).toHaveValue(500);
    expect(screen.getByLabelText(/start date/i)).toHaveValue("2023-10-01");
    expect(screen.getByLabelText(/end date/i)).toHaveValue("2023-10-31");
    expect(screen.getByLabelText(/seller/i)).toHaveValue("Test Seller");
    expect(screen.getByLabelText(/notes/i)).toHaveValue("Test Notes");
  });

  test("submits the form to create a new campaign", async () => {
    (useCreateCampaignMutation as jest.Mock).mockReturnValue({
      mutateAsync: mockCreateCampaign,
    });

    setup({ ...defaultProps, isUpdate: false });

    fireEvent.change(screen.getByLabelText(/ad ops person/i), {
      target: { value: "Jane Smith" },
    });
    expect(screen.getByLabelText(/ad ops person/i)).toHaveValue("Jane Smith");

    fireEvent.change(screen.getByLabelText(/impressions sold/i), {
      target: { value: 1000 },
    });
    expect(screen.getByLabelText(/impressions sold/i)).toHaveValue(1000);

    fireEvent.change(screen.getByLabelText(/net spend/i), {
      target: { value: 500 },
    });
    expect(screen.getByLabelText(/net spend/i)).toHaveValue(500);

    fireEvent.change(screen.getByLabelText(/seller/i), {
      target: { value: "Some Seller" },
    });
    expect(screen.getByLabelText(/seller/i)).toHaveValue("Some Seller");

    fireEvent.change(screen.getByLabelText(/notes/i), {
      target: { value: "Campaign notes here." },
    });
    expect(screen.getByLabelText(/notes/i)).toHaveValue("Campaign notes here.");

    fireEvent.change(screen.getByLabelText(/start date/i), {
      target: { value: "2023-10-01" },
    });
    expect(screen.getByLabelText(/start date/i)).toHaveValue("2023-10-01");

    fireEvent.change(screen.getByLabelText(/end date/i), {
      target: { value: "2023-10-31" },
    });
    expect(screen.getByLabelText(/end date/i)).toHaveValue("2023-10-31");

    const dealInput = screen.getByLabelText(/deal/i);
    fireEvent.mouseDown(dealInput);

    await waitFor(() => {
      expect(screen.getByText(/Deal 1 - Boyd Inc/i)).toBeInTheDocument();
    });
    const dealOptions = await screen.findAllByRole("option");
    expect(dealOptions).toHaveLength(2);

    fireEvent.click(screen.getByText(/Deal 1 - Boyd Inc/i));

    expect(dealInput).toHaveValue("Deal 1 - Boyd Inc");

    const submitButton = await screen.findByRole("button", { name: /submit/i });
    expect(submitButton).toBeInTheDocument();

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateCampaign).toHaveBeenCalled();
    });

    expect(defaultProps.handleClose).toHaveBeenCalled();
  });
});
