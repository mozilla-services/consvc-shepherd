const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiRoutes = {
  campaigns: `${BASE_URL}/campaigns/`,
  campaign: (id: number | undefined) => `${BASE_URL}/campaigns/${id}/`,
  splitCampaigns: `${BASE_URL}/campaigns/split/`,
  boostrDeals: `${BASE_URL}/deals/`,
  products: `${BASE_URL}/products/`,
};
