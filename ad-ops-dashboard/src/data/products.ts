import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { apiRoutes } from "../config/routes.config";
import { Product, Country } from "../types";

function getProducts(): Promise<Product[]> {
  return axios
    .get<Product[]>(apiRoutes.products)
    .then((response) => response.data);
}

function getCountries(): Promise<Country[]> {
  return axios
    .get<Country[]>(apiRoutes.countries)
    .then((response) => response.data);
}

export const useGetProductsQuery = () => {
  return useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
  });
};

export const useGetCountriesQuery = () => {
  return useQuery({
    queryKey: ["countries"],
    queryFn: getCountries,
  });
};
