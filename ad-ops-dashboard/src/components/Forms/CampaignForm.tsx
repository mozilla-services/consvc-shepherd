import { useEffect, useState } from "react";

import { Box, Button } from "@mui/material";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  campaignFormSchema,
  CampaignFormSchema,
} from "../../utils/schemas/campaignFormSchema";
import { BoostrDeal } from "../../types";
import TextInput from "../../components/Inputs/TextInput";
import SelectInput from "../../components/Inputs/SelectInput";
import DateInput from "../../components/Inputs/DateInput";
import {
  useCreateCampaignMutation,
  useUpdateCampaignMutation,
} from "../../data/campaigns";
import { useGetBoostDealsQuery } from "../../data/deals";

interface CampaignFormProps {
  formData: CampaignFormSchema;
  isUpdate: boolean;
  handleClose: () => void;
  campaigns: CampaignFormSchema[];
}

export default function CampaignForm({
  formData,
  isUpdate,
  handleClose,
  campaigns,
}: CampaignFormProps) {
  const { control, reset, handleSubmit, watch, setValue } =
    useForm<CampaignFormSchema>({
      resolver: zodResolver(campaignFormSchema),
      defaultValues: {
        notes: formData.notes,
        ad_ops_person: formData.ad_ops_person,
        kevel_flight_id: formData.kevel_flight_id,
        impressions_sold: formData.impressions_sold,
        net_spend: formData.net_spend,
        start_date: formData.start_date,
        end_date: formData.end_date,
        seller: formData.seller,
        deal: formData.deal,
        campaign_fields: [],
      },
    });

  const createCampaign = useCreateCampaignMutation();
  const { data: boostrDeals } = useGetBoostDealsQuery();
  const updateCampaign = useUpdateCampaignMutation(formData.id);

  const watchDeal = watch("deal");
  const [filteredCampaigns, setFilteredCampaigns] = useState<
    CampaignFormSchema[]
  >([]);

  useEffect(() => {
    let selectedDeal = watchDeal;

    if (isUpdate) {
      selectedDeal = formData.deal === watchDeal ? formData.deal : watchDeal;
    }

    if (Array.isArray(campaigns) && selectedDeal) {
      const filtered = campaigns
        .filter((item) => item.deal === selectedDeal)
        .filter((item) => !isUpdate || item.id !== formData.id);
      setFilteredCampaigns(filtered);

      setValue(
        "campaign_fields",
        filtered.map((campaign) => ({
          impressions_sold: campaign.impressions_sold,
          net_spend: campaign.net_spend,
        }))
      );
    }
  }, [watchDeal, isUpdate, setValue]);

  useFieldArray({
    control,
    name: "campaign_fields",
  });

  const onSubmitHandler = async (data: CampaignFormSchema) => {
    const updated_campaign_fields = (data.campaign_fields ?? []).map(
      (field, index) => ({
        ...field,
        campaign_id: filteredCampaigns[index]?.id,
      })
    );

    const finalData = {
      ...data,
      campaign_fields: updated_campaign_fields,
    };

    try {
      if (isUpdate) {
        await updateCampaign.mutateAsync(finalData);
      } else {
        await createCampaign.mutateAsync(finalData);
      }

      reset();
      handleClose();
    } catch (error) {
      console.error("Submission error:", error);
    }
  };

  const deals = Array.isArray(boostrDeals)
    ? boostrDeals.map((deal: BoostrDeal) => ({
        label: deal.name,
        value: deal.id,
      }))
    : [];

  return (
    <Box>
      <Box component="form" onSubmit={handleSubmit(onSubmitHandler)}>
        <Box mt={2}>
          <TextInput
            name="ad_ops_person"
            label="Ad Ops Person"
            control={control}
            fullWidth
          />
        </Box>
        <Box mt={2}>
          <TextInput
            name="kevel_flight_id"
            label="Kevel Flight Id"
            control={control}
            type="number"
            fullWidth
          />
        </Box>
        <Box mt={2}>
          <TextInput
            name="impressions_sold"
            label="Impressions Sold"
            control={control}
            type="number"
            fullWidth
          />
        </Box>
        <Box mt={2}>
          <TextInput
            name="net_spend"
            label="Net Spend"
            control={control}
            type="number"
            fullWidth
          />
        </Box>
        <Box mt={2}>
          <TextInput name="seller" label="Seller" control={control} fullWidth />
        </Box>
        <Box mt={2}>
          <DateInput
            control={control}
            name="start_date"
            format="YYYY-MM-DD"
            label="Start Date"
          />
        </Box>
        <Box mt={2}>
          <DateInput
            control={control}
            name="end_date"
            format="YYYY-MM-DD"
            label="End Date"
          />
        </Box>
        <Box mt={2}>
          <TextInput
            name="notes"
            label="Notes"
            control={control}
            rows={3}
            multiline
            fullWidth
          />
        </Box>
        <Box mt={2}>
          <SelectInput
            control={control}
            label="Deal"
            name="deal"
            options={deals || []}
          />
        </Box>

        {filteredCampaigns.length > 0 && (
          <Box
            display="flex"
            flexDirection="row"
            flexWrap="wrap"
            mt={2}
            gap={2}
          >
            {filteredCampaigns.map((field, index) => (
              <Box
                key={field.id}
                display="flex"
                flexDirection="row"
                gap={2}
                alignItems="center"
              >
                <TextInput
                  name={`campaign_fields[${index}].impressions_sold`}
                  label="Impressions Sold"
                  control={control}
                  type="number"
                />
                <TextInput
                  name={`campaign_fields[${index}].net_spend`}
                  label="Net Spend"
                  control={control}
                  type="number"
                />
              </Box>
            ))}
          </Box>
        )}

        <Box marginTop="2rem">
          <Button type="submit" variant="contained">
            Submit
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
