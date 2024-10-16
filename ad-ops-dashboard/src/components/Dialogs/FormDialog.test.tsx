import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";
import FormDialog from "./FormDialog";

describe("<FormDialog />", () => {
  const mockHandleClose = jest.fn();
  const title = "Form Title";
  const content = "This is the dialog content.";
  const actions = <button>Custom Action</button>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders FormDialog with title and content", () => {
    render(
      <FormDialog open={true} handleClose={mockHandleClose}>
        {content}
      </FormDialog>
    );

    expect(screen.getByText(content)).toBeInTheDocument();
  });

  test("calls handleClose when close button is clicked", () => {
    render(
      <FormDialog title={title} open={true} handleClose={mockHandleClose}>
        {content}
      </FormDialog>
    );

    fireEvent.click(screen.getByTestId("CloseIcon"));

    expect(mockHandleClose).toHaveBeenCalledTimes(1);
  });

  test("renders actions when provided", () => {
    render(
      <FormDialog open={true} handleClose={mockHandleClose} actions={actions}>
        {content}
      </FormDialog>
    );

    expect(screen.getByText("Custom Action")).toBeInTheDocument();
  });

  test("does not render dialog when open is false", () => {
    render(
      <FormDialog open={false} handleClose={mockHandleClose}>
        {content}
      </FormDialog>
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
