import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import App from "../App";

describe("<App />", () => {
  test("Sanity check", () => {
    expect(true).toBe(true);
  });

  test("shows the loading screen", () => {
    render(<App />);
    const header = screen.getByText("Loading...");
    expect(header).toBeInTheDocument();
  });
});
