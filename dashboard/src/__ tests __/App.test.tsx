// import { render, screen } from "@testing-library/react";
// import App from "../App";

// test("demo", () => {
//   expect(true).toBe(true);
// });

// describe("App", () => {
//   it("should work as expected", () => {
//     // render(<App />);
//     expect(1 + 1).toBe(2);
//   });
// });

import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import App from "../App";

test("demo", () => {
  expect(true).toBe(true);
});

test("Renders the main page", () => {
  render(<App />);
  expect(true).toBeTruthy();
});
