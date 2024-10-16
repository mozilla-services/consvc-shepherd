import { renderHook, waitFor } from "@testing-library/react";
import { server } from "../server";
import { createWrapper, TEST_URL } from "../__ tests __/utils";
import { useGetProductsQuery } from "../data/products";
import { http, HttpResponse } from "msw";
import { products } from "../fixtures/productFixtures";

describe("useGetProductsQuery", () => {
  test("successful query hook", async () => {
    const { result } = renderHook(() => useGetProductsQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toStrictEqual(products);
  });

  test("failure query hook", async () => {
    server.use(
      http.get(`${TEST_URL}/products/`, () => {
        return HttpResponse.json({ success: false }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useGetProductsQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});
