import React from "react";
import { Box, Button, Grid2 } from "@mui/material";
import { Add, Remove } from "@mui/icons-material";
import { Control, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { styled } from "@mui/system";
import {
  CampaignFormSchema,
  SplitFormSchema,
  splitFormSchema,
} from "../../utils/schemas/campaignFormSchema";
import TextInput from "../Inputs/TextInput";
import DateInput from "../Inputs/DateInput";
import { useSplitCampaignMutation } from "../../data/campaigns";
import Tooltip from "@mui/material/Tooltip";

interface SplitCampaignProps {
  handleClose: () => void;
  formData: CampaignFormSchema;
}

interface CampaignFormFieldsProps {
  control: Control;
  index: number;
  removeCampaign: (index: number) => void;
  appendCampaign: (data: CampaignFormSchema) => void;
  formData: CampaignFormSchema;
}

interface KevelFlightFieldsProps {
  control: Control;
  campaignIndex: number;
}

const StyledBox = styled(Box)(() => ({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
}));

const StyledButton = styled(Button)(() => ({
  marginRight: "3.8rem",
}));

export default function SplitCampaignForm({
  formData,
  handleClose,
}: SplitCampaignProps) {
  const splitMutation = useSplitCampaignMutation();

  const { control, handleSubmit, reset } = useForm<SplitFormSchema>({
    resolver: zodResolver(splitFormSchema),
    defaultValues: {
      campaigns: [
        {
          id: formData.id,
          impressions_sold: formData.impressions_sold || "",
          net_spend: formData.net_spend || "",
          flights: formData.flights ?? [{ kevel_flight_id: "" }],
          ad_ops_person: formData.ad_ops_person ?? "",
          seller: formData.seller || "",
          start_date: formData.start_date || "",
          end_date: formData.end_date || "",
          notes: formData.notes ?? "",
          deal: formData.deal || undefined,
        },
      ],
    },
  });

  const onSubmitHandler = async (data: SplitFormSchema) => {
    const updatedData = {
      ...data,
      campaigns: data.campaigns.map((campaign) => ({
        ...campaign,
        notes: campaign.notes?.trim() !== "" ? campaign.notes : null,
        ad_ops_person:
          campaign.ad_ops_person?.trim() !== "" ? campaign.ad_ops_person : null,
        flights: campaign.flights.filter(
          (flight) => flight.kevel_flight_id !== ""
        ),
      })),
      deal: formData.deal,
    };

    try {
      await splitMutation.mutateAsync(updatedData);
      reset();
      handleClose();
    } catch (error) {
      console.error("Submission error:", error);
    }
  };

  const { fields, append, remove } = useFieldArray({
    control,
    name: "campaigns",
  });

  return (
    <Box mt="2rem">
      <Box component="form" onSubmit={handleSubmit(onSubmitHandler)}>
        <Grid2 container spacing={2}>
          {fields.map((field, index) => (
            <React.Fragment key={field.id}>
              <CampaignFormFields
                control={control}
                index={index}
                removeCampaign={remove}
                appendCampaign={append}
                formData={formData}
              />
              <KevelFlightFields control={control} campaignIndex={index} />
            </React.Fragment>
          ))}
        </Grid2>
        <Box mt="2rem" display="flex" justifyContent="flex-end" width="100%">
          <StyledButton variant="contained" type="submit">
            Save
          </StyledButton>
        </Box>
      </Box>
    </Box>
  );
}

function CampaignFormFields({
  control,
  index,
  removeCampaign,
  appendCampaign,
  formData,
}: CampaignFormFieldsProps) {
  return (
    <>
      <Grid2 size={12} container spacing={3}>
        <Grid2 size={2}>
          <TextInput
            name={`campaigns.${index.toString()}.ad_ops_person`}
            label="Ad Ops Person"
            control={control}
            fullWidth
          />
        </Grid2>
        <Grid2 size={1}>
          <TextInput
            name={`campaigns.${index.toString()}.impressions_sold`}
            label="Impressions Sold"
            type="number"
            control={control}
            fullWidth
          />
        </Grid2>
        <Grid2 size={1}>
          <TextInput
            name={`campaigns.${index.toString()}.net_spend`}
            label="Net spend"
            type="number"
            control={control}
            fullWidth
          />
        </Grid2>
        <Grid2 size={2}>
          <TextInput
            name={`campaigns.${index.toString()}.seller`}
            label="Seller"
            control={control}
            fullWidth
          />
        </Grid2>
        <Grid2 size={3}>
          <StyledBox>
            <Box>
              <DateInput
                control={control}
                label="Start Date"
                name={`campaigns.${index.toString()}.start_date`}
              />
            </Box>
            <Box sx={{ marginLeft: "1rem" }}>
              <DateInput
                control={control}
                label="End Date"
                name={`campaigns.${index.toString()}.end_date`}
              />
            </Box>
          </StyledBox>
        </Grid2>
        <Grid2 size={2}>
          <StyledBox>
            <Box>
              <TextInput
                name={`campaigns.${index.toString()}.notes`}
                label="Notes"
                control={control}
              />
            </Box>
            <Box>
              {index === 0 ? (
                <Tooltip title="Add Campaign" placement="top" arrow>
                  <Button
                    onClick={() => {
                      appendCampaign({
                        impressions_sold: "",
                        net_spend: "",
                        ad_ops_person: "",
                        seller: "",
                        start_date: "",
                        end_date: "",
                        notes: "",
                        flights: [{ kevel_flight_id: "" }],
                        deal: formData.deal,
                      });
                    }}
                  >
                    <Add fontSize="large" />
                  </Button>
                </Tooltip>
              ) : (
                <Tooltip title="Remove Campaign" placement="top" arrow>
                  <Button
                    onClick={() => {
                      removeCampaign(index);
                    }}
                  >
                    <Remove fontSize="large" color="error" />
                  </Button>
                </Tooltip>
              )}
            </Box>
          </StyledBox>
        </Grid2>
      </Grid2>
    </>
  );
}

function KevelFlightFields({ control, campaignIndex }: KevelFlightFieldsProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: `campaigns.${campaignIndex.toString()}.flights`,
  });

  return (
    <Grid2
      container
      sx={{ display: "flex", alignItems: "center" }}
      spacing={2}
      mb={2}
    >
      {fields.map((item, flightIndex) => (
        <Box key={item.id || flightIndex} display="flex" alignItems="center">
          <TextInput
            name={`campaigns.${campaignIndex.toString()}.flights[${flightIndex.toString()}].kevel_flight_id`}
            label="Kevel Flight Id"
            control={control}
            type="number"
            fullWidth
            size="small"
          />
          <Tooltip title="Remove Flight" placement="top" arrow>
            <Button
              onClick={() => {
                remove(flightIndex);
              }}
            >
              <Remove fontSize="large" color="error" />
            </Button>
          </Tooltip>
        </Box>
      ))}
      <Tooltip title="Add Flight" placement="top" arrow>
        <StyledButton
          variant="contained"
          onClick={() => {
            append({ kevel_flight_id: "" });
          }}
        >
          <Add />
        </StyledButton>
      </Tooltip>
    </Grid2>
  );
}
