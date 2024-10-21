import { renderHook, waitFor } from "@testing-library/react";
import { server } from "../server";
import { createWrapper, TEST_URL } from "../__ tests __/utils";
import {
  useGetCampaignsQuery,
  useCreateCampaignMutation,
  useUpdateCampaignMutation,
  useDeleteCampaignMutation,
  useSplitCampaignMutation,
  useGetCampaignsOverviewQuery,
} from "./campaigns";
import { http, HttpResponse } from "msw";
import {
  campaigns,
  newCampaign,
  campaignOverviewData,
  updatedCampaign,
} from "../fixtures/campaignFixtures";

describe("useGetCampaignsOverviewQuery", () => {
  const filters = {};

  test("successful campaign summary fetch", async () => {
    const { result } = renderHook(() => useGetCampaignsOverviewQuery(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toStrictEqual(campaignOverviewData);
  });

  test("failure campaign summary fetch", async () => {
    server.use(
      http.get(`${TEST_URL}/campaign/overview/`, () => {
        return HttpResponse.json({ success: false }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useGetCampaignsOverviewQuery(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

describe("useGetCampaignsQuery", () => {
  test("successful query hook", async () => {
    const { result } = renderHook(() => useGetCampaignsQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toStrictEqual(campaigns);
  });

  test("failure query hook", () => {
    server.use(
      http.get(`${TEST_URL}/campaign/`, () => {
        return HttpResponse.json({ success: false }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useGetCampaignsQuery(), {
      wrapper: createWrapper(),
    });

    expect(result.current.error).toBeDefined();
  });
});

describe("useCreateCampaignMutation", () => {
  test("successful campaign addition", async () => {
    const { result } = renderHook(() => useCreateCampaignMutation(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync(newCampaign);
    const { result: campaignsResult } = renderHook(
      () => useGetCampaignsQuery(),
      {
        wrapper: createWrapper(),
      }
    );

    await waitFor(() => {
      expect(campaignsResult.current.isSuccess).toBe(true);
    });
  });

  test("count validation error on campaign creation", async () => {
    server.use(
      http.post(`${TEST_URL}/campaigns/`, () => {
        return HttpResponse.json({ success: false }, { status: 400 });
      })
    );
    const { result } = renderHook(() => useCreateCampaignMutation(), {
      wrapper: createWrapper(),
    });
    await expect(result.current.mutateAsync(newCampaign)).rejects.toBeDefined();
    await expect(
      result.current.mutateAsync(newCampaign)
    ).rejects.toHaveProperty("response.status", 400);
    await expect(result.current.mutateAsync(newCampaign)).rejects.toThrow(
      /400/
    );
  });
});

describe("useUpdateCampaignMutation", () => {
  test("successful campaign update", async () => {
    const campaignId = 1;

    const { result } = renderHook(() => useUpdateCampaignMutation(campaignId), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync(updatedCampaign);
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
  test("count validation error on campaign update", async () => {
    server.use(
      http.patch(`${TEST_URL}/campaigns/:id`, () => {
        return HttpResponse.json({ success: false }, { status: 400 });
      })
    );

    const campaignId = 1;

    const { result } = renderHook(() => useUpdateCampaignMutation(campaignId), {
      wrapper: createWrapper(),
    });
    await expect(
      result.current.mutateAsync(updatedCampaign)
    ).rejects.toBeDefined();
    await expect(
      result.current.mutateAsync(updatedCampaign)
    ).rejects.toHaveProperty("response.status", 400);
    await expect(result.current.mutateAsync(updatedCampaign)).rejects.toThrow(
      /400/
    );
  });
});

describe("useDeleteCampaignMutation", () => {
  test("successful campaign deletion", async () => {
    const campaignId = 1;

    const { result } = renderHook(() => useDeleteCampaignMutation(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      result.current.mutate(campaignId);
    });

    const { result: campaignsResult } = renderHook(
      () => useGetCampaignsQuery(),
      {
        wrapper: createWrapper(),
      }
    );

    await waitFor(() => {
      expect(campaignsResult.current.isSuccess).toBe(true);
    });
  });
});

describe("useSplitCampaignMutation", () => {
  test("successful campaign deletion", async () => {
    const splitCampaign = {
      campaigns: [
        {
          id: 7,
          notes: "Indeed drug history home.",
          ad_ops_person: "Beth Flores",
          kevel_flight_id: 7,
          impressions_sold: 2367081,
          net_spend: 195696,
          deal: 1,
          start_date: "2024-09-14",
          end_date: "2024-12-17",
          seller: "Mercado-Adams",
        },
      ],
      deal: 1,
    };
    const { result } = renderHook(() => useSplitCampaignMutation(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync(splitCampaign);
    const { result: campaignsResult } = renderHook(
      () => useGetCampaignsQuery(),
      {
        wrapper: createWrapper(),
      }
    );

    await waitFor(() => {
      expect(campaignsResult.current.isSuccess).toBe(true);
    });
  });
  test("count validation error on split campaign", async () => {
    server.use(
      http.post(`${TEST_URL}/campaigns/split/`, () => {
        return HttpResponse.json({ success: false }, { status: 400 });
      })
    );

    const splitCampaign = {
      campaigns: [
        {
          id: 7,
          notes: "Indeed drug history home.",
          ad_ops_person: "Beth Flores",
          kevel_flight_id: 7,
          impressions_sold: 2367081,
          net_spend: 195696,
          deal: 1,
          start_date: "2024-09-14",
          end_date: "2024-12-17",
          seller: "Mercado-Adams",
        },
      ],
      deal: 1,
    };

    const { result } = renderHook(() => useSplitCampaignMutation(), {
      wrapper: createWrapper(),
    });

    await expect(
      result.current.mutateAsync(splitCampaign)
    ).rejects.toBeDefined();
    await expect(
      result.current.mutateAsync(splitCampaign)
    ).rejects.toHaveProperty("response.status", 400);
    await expect(result.current.mutateAsync(splitCampaign)).rejects.toThrow(
      /400/
    );
  });
});
