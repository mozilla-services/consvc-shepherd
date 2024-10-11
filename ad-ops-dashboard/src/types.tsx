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

export interface Campaign {
  id: number;
  ad_ops_person: string;
  notes: string;
  kevel_flight_id: number;
  net_spend: number;
  impressions_sold: number;
  seller: string;
  start_date: string;
  end_date: string;
  created_on: string;
  updated_on: string;
  deal: number;
}

export interface BoostrDeal {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  boostr_id: number;
  full_name: string;
  country: string;
  campaign_type: string;
  created_on: string;
  updated_on: string;
}
