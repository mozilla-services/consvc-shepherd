import { Product } from "./types";

export const getProducts = async (): Promise<Product[]> => {
  try {
    const response = await fetch("http://localhost:7001/api/v1/products");
    const products = (await response.json()) as Product[];
    return products;
  } catch (error) {
    console.error(error);
    return [];
  }
};
