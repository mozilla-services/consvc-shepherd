import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Campaign from "./Campaign";
import { useGetCampaignsQuery } from "../../data/campaigns";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useDeleteCampaignMutation } from "../../data/campaigns";

jest.mock("../../data/campaigns");
jest.mock("../../components/AppLoader/AppLoader", () => {
  const MockAppLoader = () => <div>Loading...</div>;
  MockAppLoader.displayName = "AppLoader";
  return MockAppLoader;
});

jest.mock("../../components/Dialogs/FormDialog", () => {
  interface MockFormDialogProps {
    open: boolean;
    children: React.ReactNode;
  }

  const MockFormDialog = ({ open, children }: MockFormDialogProps) => {
    return open ? <div data-testid="form-dialog">{children}</div> : null;
  };

  MockFormDialog.displayName = "MockFormDialog";

  return MockFormDialog;
});

jest.mock("../../components/Dialogs/ConfirmationDialog", () => {
  interface ConfirmationDialogProps {
    openConfirmation: boolean;
    handleOk: () => void;
    handleClose: () => void;
  }
  const MockConfirmationDialog = ({
    openConfirmation,
    handleOk,
    handleClose,
  }: ConfirmationDialogProps) => {
    return openConfirmation ? (
      <div data-testid="confirmation-dialog">
        <button onClick={handleOk}>Confirm</button>
        <button onClick={handleClose}>Cancel</button>
      </div>
    ) : null;
  };

  MockConfirmationDialog.displayName = "ConfirmationDialog";

  return MockConfirmationDialog;
});

jest.mock("../../components/Buttons/ActionButton", () => {
  interface ActionButtonProps {
    icon: string;
    handleClick: () => void;
  }

  const MockActionButton = ({ icon, handleClick }: ActionButtonProps) => {
    return (
      <button onClick={handleClick} data-testid="action-button">
        {icon}
      </button>
    );
  };

  MockActionButton.displayName = "ActionButton";

  return MockActionButton;
});

const queryClient = new QueryClient();

describe("<Campaign />", () => {
  const mockCampaignData = [
    {
      id: 1,
      notes: "Test Note 1",
      ad_ops_person: "Person 1",
      kevel_flight_id: "KF1",
      impressions_sold: 1000,
      net_spend: 100,
      seller: "Seller 1",
    },
    {
      id: 2,
      notes: "Test Note 2",
      ad_ops_person: "Person 2",
      kevel_flight_id: "KF2",
      impressions_sold: 2000,
      net_spend: 200,
      seller: "Seller 2",
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  test("renders loading screen when fetching data", () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({ isFetching: true });
    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  test("renders error message when fetching data fails", () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      error: { message: "Error occurred" },
    });
    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );

    expect(
      screen.getByText("An error has occurred: Error occurred")
    ).toBeInTheDocument();
  });

  test("renders campaign data in the table", () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      data: mockCampaignData,
    });
    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );
    expect(screen.getByText("Test Note 1")).toBeInTheDocument();
    expect(screen.getByText("Person 1")).toBeInTheDocument();
    expect(screen.getByText("Seller 1")).toBeInTheDocument();
  });

  test("opens form dialog when Add Data button is clicked", async () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      data: mockCampaignData,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );
    fireEvent.click(screen.getByText("Add Data"));
    await waitFor(() => {
      expect(screen.getByTestId("form-dialog")).toBeInTheDocument();
    });
  });

  test("opens confirmation dialog and calls delete mutation on confirm", async () => {
    const mockDeleteCampaign = jest.fn();
    (useDeleteCampaignMutation as jest.Mock).mockReturnValue({
      mutate: mockDeleteCampaign,
    });
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      data: mockCampaignData,
    });
    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );

    const deleteButton = screen.getAllByTestId("action-button")[1];
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByTestId("confirmation-dialog")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Confirm"));
    await waitFor(() => {
      expect(mockDeleteCampaign).toHaveBeenCalled();
    });
  });

  test("opens form dialog with correct data when editing a campaign", async () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      data: mockCampaignData,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );

    const editButton = screen.getAllByTestId("action-button")[0];
    fireEvent.click(editButton);

    await waitFor(() => {
      expect(screen.getByTestId("form-dialog")).toBeInTheDocument();
    });

    expect(screen.getByTestId("form-dialog")).toHaveTextContent("Test Note 1");
  });

  test("opens split campaign modal when split button is clicked", async () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      data: mockCampaignData,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );

    const splitButton = screen.getAllByTestId("action-button")[2];
    fireEvent.click(splitButton);

    await waitFor(() => {
      expect(screen.getByTestId("form-dialog")).toBeInTheDocument();
    });

    expect(screen.getByTestId("form-dialog")).toHaveTextContent(
      "Ad Ops Person"
    );
  });

  test("closes confirmation dialog without action when cancelled", async () => {
    (useGetCampaignsQuery as jest.Mock).mockReturnValue({
      data: mockCampaignData,
    });
    render(
      <QueryClientProvider client={queryClient}>
        <Campaign />
      </QueryClientProvider>
    );

    const deleteButton = screen.getAllByTestId("action-button")[1];
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByTestId("confirmation-dialog")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Cancel"));
    await waitFor(() => {
      expect(
        screen.queryByTestId("confirmation-dialog")
      ).not.toBeInTheDocument();
    });
  });
});
