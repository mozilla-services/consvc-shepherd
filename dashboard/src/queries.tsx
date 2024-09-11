import { Product, ProductResponse } from "./types";

export const getProducts = async (): Promise<Product[]> => {
  try {
    const response = await fetch("http://localhost:8000/api/v1/products");
    const json = await response.json();
    const products: Product[] = json.map((data: ProductResponse) => {
      const product: Product = {
        name: data.full_name,
        country: data.country,
        campaign_type: data.campaign_type,
      };
      return product;
    });
    return Promise.resolve(products);
  } catch (error) {
    return Promise.reject(error);
  }
};
