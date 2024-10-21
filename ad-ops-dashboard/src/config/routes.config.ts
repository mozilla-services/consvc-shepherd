const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiRoutes = {
  campaigns: `${BASE_URL}/campaigns/`,
  splitCampaigns: `${BASE_URL}/campaigns/split/`,
  campaign: (id: number) => `${BASE_URL}/campaigns/${id.toString()}/`,
  campaignOverview: `${BASE_URL}/campaign/overview/`,
  boostrDeals: `${BASE_URL}/deals/`,
  advertisers: `${BASE_URL}/deals/advertisers/`,
  products: `${BASE_URL}/products/`,
  countries: `${BASE_URL}/products/countries/`,
};
