import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";

export const useGetBoostDealsQuery = () => {
  const data = useQuery({
    queryKey: ["boostrDeals"],
    queryFn: async () => {
      const { data } = await axios.get(apiRoutes.boostrDeals);
      return data;
    },
  });

  return data;
};
