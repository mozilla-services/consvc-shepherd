import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios, { AxiosError } from "axios";
import { toast } from "react-toastify";
import { apiRoutes } from "../config/routes.config";
import {
  CampaignFormSchema,
  SplitFormSchema,
} from "../utils/schemas/campaignFormSchema";
import {
  ErrorResponse,
  Campaign,
  CampaignFilters,
  CampaignOverview,
} from "../types";

function fetchCampaign(): Promise<Campaign[]> {
  return axios
    .get<Campaign[]>(apiRoutes.campaigns)
    .then((response) => response.data);
}

export const useGetCampaignsQuery = () => {
  return useQuery({
    queryKey: ["campaigns"],
    queryFn: fetchCampaign,
  });
};

function getCampaignOverview(filters: CampaignFilters) {
  const { months, country, products, advertisers, search } = filters;

  const queryParams = new URLSearchParams();

  const addQueryParam = (key: string, value?: string) => {
    if (value != undefined) queryParams.append(key, value);
  };

  addQueryParam("month", months);
  addQueryParam("country", country);
  addQueryParam("placement", products);
  addQueryParam("advertiser", advertisers);
  addQueryParam("search", search);

  return axios
    .get<CampaignOverview[]>(`${apiRoutes.campaignOverview}?${queryParams}`)
    .then((response) => response.data);
}

export const useGetCampaignsOverviewQuery = (filters: CampaignFilters) => {
  return useQuery({
    queryKey: ["campaignsOverview", filters],
    queryFn: () => getCampaignOverview(filters),
  });
};

export const useSplitCampaignMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SplitFormSchema) => {
      return axios.post(apiRoutes.splitCampaigns, data);
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      const nonFieldErrors = error.response?.data.non_field_errors;

      let errorMessage: string;

      if (
        nonFieldErrors &&
        Array.isArray(nonFieldErrors) &&
        nonFieldErrors.length > 0
      ) {
        errorMessage = nonFieldErrors[0];
      } else {
        errorMessage = "An unexpected error occurred";
      }
      toast.error(errorMessage);
    },
    onSuccess: async () => {
      toast.success("Campaign splitted successfully.");
      await queryClient.invalidateQueries({ queryKey: ["campaigns"] });
    },
  });
};

export const useCreateCampaignMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CampaignFormSchema) => {
      return axios.post(apiRoutes.campaigns, data);
    },
    onMutate: (data) => {
      return data;
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      const nonFieldErrors = error.response?.data.non_field_errors;

      let errorMessage: string;
      if (
        nonFieldErrors &&
        Array.isArray(nonFieldErrors) &&
        nonFieldErrors.length > 0
      ) {
        errorMessage = nonFieldErrors[0];
      } else {
        errorMessage = "An unexpected error occurred";
      }
      toast.error(errorMessage);
    },
    onSuccess: async (data) => {
      toast.success("Campaign added successfully.");
      await queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      return data;
    },
  });
};

export const useUpdateCampaignMutation = (id: number | undefined) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CampaignFormSchema) => {
      return axios.patch(apiRoutes.campaign(id), data);
    },
    onMutate: (data) => {
      return data;
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      const nonFieldErrors = error.response?.data.non_field_errors;

      let errorMessage: string;

      if (
        nonFieldErrors &&
        Array.isArray(nonFieldErrors) &&
        nonFieldErrors.length > 0
      ) {
        errorMessage = nonFieldErrors[0];
      } else {
        errorMessage = "An unexpected error occurred";
      }
      toast.error(errorMessage);
    },
    onSuccess: async (data) => {
      toast.success("Campaign updated successfully.");
      await queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      return data;
    },
  });
};

export const useDeleteCampaignMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number | undefined) => {
      return axios.delete(apiRoutes.campaign(id));
    },
    onMutate: (data) => {
      return data;
    },
    onError: (error) => {
      toast.error(error.message);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      toast.success("Campaign deleted successfully.");
    },
  });
};
