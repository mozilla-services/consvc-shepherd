import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";
import { BoostrDeal } from "../types";

function getDeals(): Promise<BoostrDeal[]> {
  return axios
    .get<BoostrDeal[]>(apiRoutes.boostrDeals)
    .then((response) => response.data);
}

export const useGetBoostDealsQuery = () => {
  const data = useQuery({
    queryKey: ["boostrDeals"],
    queryFn: getDeals,
  });

  return data;
};
