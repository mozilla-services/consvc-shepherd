import { renderHook, waitFor } from "@testing-library/react";
import { server } from "../server";
import { createWrapper, TEST_URL } from "../__ tests __/utils";
import { useGetBoostDealsQuery, useGetAdvertisersQuery } from "./deals";
import { http, HttpResponse } from "msw";
import { deals, advertisers } from "../fixtures/dealFixtures";

describe("useGetBoostDealsQuery", () => {
  test("successful query hook", async () => {
    const { result } = renderHook(() => useGetBoostDealsQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toStrictEqual(deals);
  });

  test("failure query hook", async () => {
    server.use(
      http.get(`${TEST_URL}/deals/`, () => {
        return HttpResponse.json({ success: false }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useGetBoostDealsQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

describe("useGetAdvertisersQuery", () => {
  test("successful query hook", async () => {
    const { result } = renderHook(() => useGetAdvertisersQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toStrictEqual(advertisers);
  });

  test("failure query hook", async () => {
    server.use(
      http.get(`${TEST_URL}/deals/advertisers`, () => {
        return HttpResponse.json({ success: false }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useGetAdvertisersQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});
