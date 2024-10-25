import { http, HttpResponse } from "msw";
import { products, countries } from "../fixtures/productFixtures";
import { TEST_URL } from "../__ tests __/utils";

export const productHandlers = [
  http.get(`${TEST_URL}/products/`, () => {
    return HttpResponse.json(products);
  }),
  http.get(`${TEST_URL}/products/countries`, () => {
    return HttpResponse.json(countries);
  }),
];
