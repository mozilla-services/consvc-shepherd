import { http, HttpResponse } from "msw";
import { products } from "../fixtures/productFixtures";
import { TEST_URL } from "../__ tests __/utils";

export const productHandlers = [
  http.get(`${TEST_URL}/products/`, () => {
    return HttpResponse.json(products);
  }),
];
