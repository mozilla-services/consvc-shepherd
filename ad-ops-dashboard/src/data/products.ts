import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";

export const useGetProductsQuery = () => {
  const data = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const { data } = await axios.get(apiRoutes.products);
      return data;
    },
  });

  return data;
};
