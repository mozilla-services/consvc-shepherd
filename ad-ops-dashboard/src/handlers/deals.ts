import { http, HttpResponse } from "msw";
import { deals } from "../fixtures/dealFixtures";
import { TEST_URL } from "../__ tests __/utils";

export const dealHandlers = [
  http.get(`${TEST_URL}/deals/`, () => {
    return HttpResponse.json(deals);
  }),
];
