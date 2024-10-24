import { http, HttpResponse } from "msw";
import { campaigns, campaignOverviewData } from "../fixtures/campaignFixtures";
import { CampaignOverview } from "../types";
import { TEST_URL } from "../__ tests __/utils";

export const campaignHandlers = [
  http.get(`${TEST_URL}/campaigns/`, () => {
    return HttpResponse.json(campaigns);
  }),

  http.post(`${TEST_URL}/campaigns/`, async ({ request }) => {
    const newCampaign = await request.json();

    return HttpResponse.json({ data: newCampaign }, { status: 200 });
  }),

  http.patch(`${TEST_URL}/campaigns/:id/`, async ({ request, params }) => {
    const data = await request.json();
    const { id } = params;

    if (!id) {
      return HttpResponse.json({ success: false }, { status: 401 });
    }

    return HttpResponse.json({ data: data }, { status: 200 });
  }),

  http.delete(`${TEST_URL}/campaigns/:id`, async ({ request, params }) => {
    await request.json();
    const { id } = params;

    if (!id) {
      return HttpResponse.json({ success: false }, { status: 401 });
    }

    return HttpResponse.json({ success: true }, { status: 204 });
  }),

  http.post(`${TEST_URL}/campaigns/split/`, async ({ request }) => {
    await request.json();

    return HttpResponse.json({ success: true }, { status: 201 });
  }),

  http.get(`${TEST_URL}/campaign/overview/`, () => {
    const campaignOverview: CampaignOverview[] = campaignOverviewData;
    return HttpResponse.json(campaignOverview);
  }),
];
