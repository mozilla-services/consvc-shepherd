import { server } from "./server";

import { TextDecoder, TextEncoder } from "util";

process.env.VITE_API_BASE_URL = "http://localhost-test";

Object.assign(global, { TextDecoder, TextEncoder });

beforeAll(() => {
  server.listen();
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
