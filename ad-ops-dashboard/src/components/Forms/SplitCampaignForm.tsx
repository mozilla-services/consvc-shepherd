import React from "react";
import { Box, Button, Grid2 } from "@mui/material";
import { Add, Remove } from "@mui/icons-material";
import { useFieldArray, useForm } from "react-hook-form";
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
          kevel_flight_id: formData.kevel_flight_id || "",
          ad_ops_person: formData.ad_ops_person || "",
          seller: formData.seller || "",
          start_date: formData.start_date || "",
          end_date: formData.end_date || "",
          notes: formData.notes || "",
          deal: formData.deal || undefined,
        },
      ],
    },
  });

  const onSubmitHandler = (data: SplitFormSchema) => {
    const updatedData = {
      ...data,
      deal: formData.deal,
    };

    splitMutation.mutate(updatedData, {
      onSuccess: () => {
        reset();
        handleClose();
      },
    });
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
              <Grid2 size={2}>
                <TextInput
                  name={`campaigns.${index}.ad_ops_person`}
                  label="Ad Ops Person"
                  control={control}
                />
              </Grid2>
              <Grid2 size={1}>
                <TextInput
                  name={`campaigns.${index}.kevel_flight_id`}
                  label="Kevel Flight Id"
                  type="number"
                  control={control}
                />
              </Grid2>
              <Grid2 size={1}>
                <TextInput
                  name={`campaigns.${index}.impressions_sold`}
                  label="Impressions Sold"
                  type="number"
                  control={control}
                />
              </Grid2>
              <Grid2 size={1}>
                <TextInput
                  name={`campaigns.${index}.net_spend`}
                  label="Net spend"
                  type="number"
                  control={control}
                />
              </Grid2>
              <Grid2 size={2}>
                <TextInput
                  name={`campaigns.${index}.seller`}
                  label="Seller"
                  control={control}
                />
              </Grid2>
              <Grid2 size={3}>
                <StyledBox>
                  <Box sx={{ marginLeft: "1rem" }}>
                    <DateInput
                      control={control}
                      label="Start Date"
                      name={`campaigns.${index}.start_date`}
                    />
                  </Box>
                  <Box>
                    <DateInput
                      control={control}
                      label="End Date"
                      name={`campaigns.${index}.end_date`}
                    />
                  </Box>
                </StyledBox>
              </Grid2>
              <Grid2 size={2}>
                <StyledBox>
                  <Box>
                    <TextInput
                      name={`campaigns.${index}.notes`}
                      label="Notes"
                      control={control}
                    />
                  </Box>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    {index == 0 ? (
                      <Tooltip title="Split Campaign" placement="top" arrow>
                        <Button
                          onClick={() =>
                            append({
                              impressions_sold: "",
                              net_spend: "",
                              kevel_flight_id: "",
                              ad_ops_person: "",
                              seller: "",
                              start_date: "",
                              end_date: "",
                              notes: "",
                              deal: formData.deal,
                            })
                          }
                        >
                          <Add fontSize="large" />
                        </Button>
                      </Tooltip>
                    ) : (
                      <Tooltip title="Remove Campaign" placement="top" arrow>
                        <Button onClick={() => remove(index)}>
                          <Remove fontSize="large" color="error" />
                        </Button>
                      </Tooltip>
                    )}
                  </Box>
                </StyledBox>
              </Grid2>
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
