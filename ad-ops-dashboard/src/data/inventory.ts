import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";

export const useGetInventoryQuery = () => {
  const getInventory = useQuery({
    queryKey: ["inventory"],
    queryFn: async () => {
      const { data } = await axios.get(apiRoutes.inventory);
      return data;
    },
  });

  return getInventory;
};