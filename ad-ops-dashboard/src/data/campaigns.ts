import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios, { AxiosError } from "axios";
import { toast } from "react-toastify";
import { apiRoutes } from "../config/routes.config";
import {
  CampaignFormSchema,
  SplitFormSchema,
} from "../utils/schemas/campaignFormSchema";
import { ErrorResponse } from "../types";

export const useGetCampaignsQuery = () => {
  const getCampaigns = useQuery({
    queryKey: ["campaigns"],
    queryFn: async () => {
      const { data } = await axios.get(apiRoutes.campaigns);
      return data;
    },
  });

  return getCampaigns;
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
    onSuccess: () => {
      toast.success("Campaign splitted successfully.");
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
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
    onError: (error: any) => {
      if (error.response?.data) {
        const errorMessage =
          error.response.data.non_field_errors?.[0] || "An error occurred";
        toast.error(errorMessage);
      } else {
        toast.error("An unexpected error occurred");
      }
    },
    onSuccess: (data) => {
      toast.success("Campaign added successfully.");
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
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
    onError: (error: any) => {
      if (error.response?.data) {
        const errorMessage =
          error.response.data.non_field_errors?.[0] || "An error occurred";
        toast.error(errorMessage);
      } else {
        toast.error("An unexpected error occurred");
      }
    },
    onSuccess: (data) => {
      toast.success("Campaign updated successfully.");
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      toast.success("Campaign deleted successfully.");
    },
  });
};
