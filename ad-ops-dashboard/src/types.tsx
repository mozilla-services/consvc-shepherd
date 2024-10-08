export interface Product {
  full_name: string;
  country: string;
  campaign_type: string;
}

export interface ProductResponse {
  full_name: string;
  country: string;
  campaign_type: string;
}

export interface CampaignField {
  impressions_sold?: number;
  net_spend?: number;
  campaign_id?: number;
}
export interface BoostrDeal {
  id: number;
  name: string;
}

export interface ErrorResponse {
  non_field_errors?: string[];
}
