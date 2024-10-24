import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";
import { BoostrDeal, Advertiser } from "../types";

function getDeals(): Promise<BoostrDeal[]> {
  return axios
    .get<BoostrDeal[]>(apiRoutes.boostrDeals)
    .then((response) => response.data);
}

function getAdvertisers(): Promise<Advertiser[]> {
  return axios
    .get<Advertiser[]>(apiRoutes.advertisers)
    .then((response) => response.data);
}

export const useGetBoostDealsQuery = () => {
  return useQuery({
    queryKey: ["boostrDeals"],
    queryFn: getDeals,
  });
};

export const useGetAdvertisersQuery = () => {
  return useQuery({
    queryKey: ["advertiser"],
    queryFn: getAdvertisers,
  });
};
