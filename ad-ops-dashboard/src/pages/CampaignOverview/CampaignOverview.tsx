import { useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef } from "ag-grid-community";
import { Box } from "@mui/material";
import AppLoader from "../../components/AppLoader/AppLoader";
import { useGetCampaignsOverviewQuery } from "../../data/campaigns";
import { styled } from "@mui/system";
import FilterCampaignOverview from "../../components/Filters/CampaignOverviewFilter";
import { CampaignFilters } from "../../types";

const TableContainer = styled(Box)`
  width: 100%;
  margin-top: 1rem;
`;

export default function CampaignOverview() {
  const [filters, setFilters] = useState({});
  const {
    data: campaignOverviewData,
    error,
    isPending,
    isFetching,
  } = useGetCampaignsOverviewQuery(filters);
  const [colDefs] = useState<ColDef[]>([
    { field: "advertiser", headerName: "Advertiser" },
    { field: "net_spend", headerName: "Budget" },
    { field: "revenue", headerName: "Revenue" },
    { field: "impressions_sold", headerName: "Impressions Sold" },
    { field: "impressions_remaining", headerName: "Impressions Remaining" },
    { field: "clicks_delivered", headerName: "Clicks Delivered" },
    { field: "ctr", headerName: "CTR" },
    { field: "net_ecpm", headerName: "Net eCPM" },
    { field: "live", headerName: "Live" },
  ]);

  const handleFilterChange = (filters: CampaignFilters) => {
    const formattedFilters = {
      months: filters.months,
      country: filters.country,
      products: filters.products,
      advertisers: filters.advertisers,
      search: filters.search,
    };
    setFilters(formattedFilters);
  };

  if (error) return "An error has occurred: " + error.message;

  const defaultColDef: ColDef = {
    flex: 1,
  };

  const isLoading = isPending || isFetching;

  return (
    <>
      <FilterCampaignOverview onFilterChange={handleFilterChange} />

      {isLoading ? (
        <AppLoader />
      ) : (
        <TableContainer className="ag-theme-quartz">
          <AgGridReact
            rowData={campaignOverviewData}
            columnDefs={colDefs}
            defaultColDef={defaultColDef}
            pagination={true}
            domLayout="autoHeight"
            paginationPageSize={10}
            paginationPageSizeSelector={[10, 20, 50, 100]}
          />
        </TableContainer>
      )}
    </>
  );
}
