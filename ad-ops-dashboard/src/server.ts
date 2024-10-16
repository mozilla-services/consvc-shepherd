import { setupServer } from "msw/node";
import { campaignHandlers } from "./handlers/campaigns";
import { dealHandlers } from "./handlers/deals";
import { productHandlers } from "./handlers/products";

export const server = setupServer(
  ...campaignHandlers,
  ...dealHandlers,
  ...productHandlers
);
