import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";
import ActionButton from "./ActionButton";

describe("<ActionButton />", () => {
  test("renders ActionButton with provided icon and calls handleClick on click", () => {
    const mockHandleClick = jest.fn();
    const testIcon = <span>Test Icon</span>;

    render(<ActionButton icon={testIcon} handleClick={mockHandleClick} />);

    expect(screen.getByText("Test Icon")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button"));

    expect(mockHandleClick).toHaveBeenCalledTimes(1);
  });
});
