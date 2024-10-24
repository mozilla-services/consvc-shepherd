import { http, HttpResponse } from "msw";
import { deals, advertisers } from "../fixtures/dealFixtures";
import { TEST_URL } from "../__ tests __/utils";

export const dealHandlers = [
  http.get(`${TEST_URL}/deals/`, () => {
    return HttpResponse.json(deals);
  }),
  http.get(`${TEST_URL}/deals/advertisers`, () => {
    return HttpResponse.json(advertisers);
  }),
];
