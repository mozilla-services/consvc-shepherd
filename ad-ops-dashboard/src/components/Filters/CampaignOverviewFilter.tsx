import { useEffect, useMemo, FC } from "react";
import { Box, Grid2 } from "@mui/material";
import DateInput from "../../components/Inputs/DateInput";
import SelectInput from "../../components/Inputs/SelectInput";
import TextInput from "../../components/Inputs/TextInput";
import { useForm } from "react-hook-form";
import { useGetProductsQuery, useGetCountriesQuery } from "../../data/products";
import { useGetAdvertisersQuery } from "../../data/deals";
import debounce from "lodash/debounce";
import { CampaignFilters } from "../../types";

interface FilterCampaignOverviewProps {
  onFilterChange: (filters: CampaignFilters) => void;
}

const FilterCampaignOverview: FC<FilterCampaignOverviewProps> = ({
  onFilterChange,
}) => {
  const { data: productData } = useGetProductsQuery();
  const { data: countriesData } = useGetCountriesQuery();
  const { data: advertisersData } = useGetAdvertisersQuery();
  const { control, watch } = useForm<CampaignFilters>();

  const months = watch("months");
  const country = watch("country");
  const products = watch("products");
  const advertisers = watch("advertisers");
  const search = watch("search");

  const debouncedOnFilterChange = useMemo(() => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
    return debounce((filters: CampaignFilters) => {
      onFilterChange(filters);
    }, 500) as (filters: CampaignFilters) => void;
  }, [onFilterChange]);

  useEffect(() => {
    const filters = { months, country, products, advertisers, search };
    debouncedOnFilterChange(filters);
  }, [months, country, products, advertisers, search]);

  const productOptions = productData?.map((product) => ({
    label: product.full_name,
    value: product.id,
  }));

  return (
    <Box component="form" sx={{ pt: 2, pb: 1 }}>
      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 6, md: 2 }}>
          <DateInput
            control={control}
            name="months"
            format="YYYY-MM"
            views={["month", "year"]}
            label="Filter By Month"
          />
        </Grid2>
        <Grid2 size={{ xs: 6, md: 2 }}>
          <SelectInput
            control={control}
            label="Filter By Countries"
            name="country"
            options={countriesData}
          />
        </Grid2>
        <Grid2 size={{ xs: 6, md: 2 }}>
          <SelectInput
            control={control}
            label="Filter By Products"
            name="products"
            options={productOptions}
          />
        </Grid2>
        <Grid2 size={{ xs: 6, md: 2 }}>
          <SelectInput
            control={control}
            label="Filter By Advertisers"
            name="advertisers"
            options={advertisersData}
          />
        </Grid2>
        <Grid2 size={{ xs: 6, md: 1 }}></Grid2>
        <Grid2 size={{ xs: 6, md: 3 }} sx={{ mt: 0 }}>
          <TextInput
            type="search"
            control={control}
            label="Search"
            name="search"
            sx={{ width: "100%" }}
          />
        </Grid2>
      </Grid2>
    </Box>
  );
};

export default FilterCampaignOverview;
