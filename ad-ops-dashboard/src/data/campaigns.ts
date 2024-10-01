import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { toast } from "react-toastify";
import { apiRoutes } from "../config/routes.config";
import { CampaignFormSchema } from "../utils/schemas/campaignFormSchema";
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
