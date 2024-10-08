const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiRoutes = {
  campaigns: `${BASE_URL}/campaigns/`,
  splitCampaigns: `${BASE_URL}/campaigns/split/`,
  campaign: (id: number) => `${BASE_URL}/campaigns/${id.toString()}/`,
  boostrDeals: `${BASE_URL}/deals/`,
  products: `${BASE_URL}/products/`,
};
