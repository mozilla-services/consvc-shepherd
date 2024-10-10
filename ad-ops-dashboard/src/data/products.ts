import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";
import { Product } from "../types";

function getProducts(): Promise<Product[]> {
  return axios
    .get<Product[]>(apiRoutes.products)
    .then((response) => response.data);
}

export const useGetProductsQuery = () => {
  const data = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
  });

  return data;
};
