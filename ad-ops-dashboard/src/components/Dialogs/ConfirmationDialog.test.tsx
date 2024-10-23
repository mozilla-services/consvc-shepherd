import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";
import ConfirmationDialog from "./ConfirmationDialog";

describe("<ConfirmationDialog />", () => {
  const mockHandleClose = jest.fn();
  const mockHandleOk = jest.fn();
  const message = "Are you sure you want to delete this item?";
  const title = "Confirm Deletion";

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders ConfirmationDialog with title and message", () => {
    render(
      <ConfirmationDialog
        openConfirmation={true}
        handleClose={mockHandleClose}
        handleOk={mockHandleOk}
        message={message}
        title={title}
      />
    );

    expect(screen.getByText(title)).toBeInTheDocument();
    expect(screen.getByText(message)).toBeInTheDocument();
  });

  test("calls handleClose when Cancel button is clicked", () => {
    render(
      <ConfirmationDialog
        openConfirmation={true}
        handleClose={mockHandleClose}
        handleOk={mockHandleOk}
        message={message}
        title={title}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));

    expect(mockHandleClose).toHaveBeenCalledTimes(1);
  });

  test("calls handleOk when Delete button is clicked", () => {
    render(
      <ConfirmationDialog
        openConfirmation={true}
        handleClose={mockHandleClose}
        handleOk={mockHandleOk}
        message={message}
        title={title}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /delete/i }));

    expect(mockHandleOk).toHaveBeenCalledTimes(1);
  });

  test("does not render dialog when openConfirmation is false", () => {
    render(
      <ConfirmationDialog
        openConfirmation={false}
        handleClose={mockHandleClose}
        handleOk={mockHandleOk}
        message={message}
        title={title}
      />
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
