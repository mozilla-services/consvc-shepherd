import { z } from "zod";
import dayjs from "dayjs";

export const campaignFormSchema = z.object({
  id: z.number().optional(),
  notes: z.string().min(5, "Notes must be at least 5 characters long"),
  ad_ops_person: z
    .string()
    .min(5, "Ad Ops person name must be at least 5 characters long"),
  kevel_flight_id: z.preprocess(
    (val) => (val === null ? undefined : Number(val)),
    z
      .union([
        z.number().min(1, "Kevel Flight ID must be a positive number"),
        z.string().optional(),
      ])
      .refine((val) => val !== undefined, {
        message: "Kevel Flight ID is required",
      })
  ),
  impressions_sold: z.preprocess(
    (val) => (val === null ? undefined : Number(val)),
    z
      .union([
        z.number().min(1, "Impressions sold must be a positive number"),
        z.string().optional(),
      ])
      .refine((val) => val !== undefined, {
        message: "Impressions sold is required",
      })
  ),
  net_spend: z.preprocess(
    (val) => (val === null ? undefined : Number(val)),
    z
      .union([
        z.number().min(1, "Net spend must be a positive number"),
        z.string().optional(),
      ])
      .refine((val) => val !== undefined, {
        message: "Net spend is required",
      })
  ),
  deal: z
    .number({
      invalid_type_error: "Deal value is required",
      required_error: "Deal is required",
    })
    .positive("Deal must be a positive number"),
  start_date: z
    .string({ required_error: "Start date is required" })
    .refine((val) => dayjs(val, "YYYY-MM-DD", true).isValid(), {
      message: "Start date is required",
    }),
  end_date: z
    .string({ required_error: "End date is required" })
    .refine((val) => dayjs(val, "YYYY-MM-DD", true).isValid(), {
      message: "Start date is required",
    }),
  seller: z.string().min(5, "Seller name must be at least 5 characters long"),
  campaign_fields: z.array(
    z.object({
      impressions_sold: z.preprocess(
        (val) => (val === null ? undefined : Number(val)),
        z
          .union([
            z.number().min(1, "Impressions sold must be a positive number"),
            z.string().optional(),
          ])
          .refine((val) => val !== undefined, {
            message: "Impressions sold is required",
          })
      ),
      net_spend: z.preprocess(
        (val) => (val === null ? undefined : Number(val)),
        z
          .union([
            z.number().min(1, "Net spend must be a positive number"),
            z.string().optional(),
          ])
          .refine((val) => val !== undefined, {
            message: "Net spend is required",
          })
      ),
    })
  ),
});

export type CampaignFormSchema = z.infer<typeof campaignFormSchema>;

export const defaultCampaignValues: CampaignFormSchema = {
  notes: "",
  ad_ops_person: "",
  kevel_flight_id: "",
  impressions_sold: "",
  net_spend: "",
  seller: "",
  deal: -1,
  start_date: "",
  end_date: "",
  campaign_fields: [],
};
