import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";

export const useGetInventoryQuery = () => {
  const getInventory = useQuery({
    queryKey: ["campaigns"],
    queryFn: async () => {
      const { data } = await axios.get(apiRoutes.campaigns);
      return data;
    },
  });

  return getInventory;
};