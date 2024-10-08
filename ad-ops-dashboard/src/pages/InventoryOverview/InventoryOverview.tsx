import { useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef } from "ag-grid-community";
import { Box } from "@mui/material";
import AppLoader from "../../components/AppLoader/AppLoader";
import { useGetInventoryQuery } from "../../data/inventory";
import { styled } from "@mui/system";

const TableContainer = styled(Box)`
  width: 100%;
  margin-top: 1rem;
`;

export default function InventoryOverview() {
  const {
    data: campaignsData,
    error,
    isPending,
    isFetching,
  } = useGetInventoryQuery();
  const [colDefs] = useState<ColDef[]>([
    { field: "impressions_sold", headerName: "Country" },
    { field: "impressions_sold", headerName: "Revenue" },
    { field: "impressions_sold", headerName: "eCPM" },
    { field: "impressions_sold", headerName: "Inv. Available" },
    { field: "impressions_sold", headerName: "Inv. Booked" },

    { field: "impressions_sold", headerName: "Inv. Unsold" },
    { field: "impressions_sold", headerName: "Inv. Remaining" },
  ]);

  if (isPending || isFetching) return <AppLoader />;

  if (error) return "An error has occurred: " + error.message;

  const defaultColDef: ColDef = {
    flex: 1,
  };

  return (
    <>
      <TableContainer className="ag-theme-quartz">
        <AgGridReact
          rowData={campaignsData || []}
          columnDefs={colDefs}
          defaultColDef={defaultColDef}
          pagination={true}
          domLayout="autoHeight"
          paginationPageSize={10}
          paginationPageSizeSelector={false}
        />
      </TableContainer>
    </>
  );
}
