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
    data: inventoryData,
    error,
    isPending,
    isFetching,
  } = useGetInventoryQuery();
  const [colDefs] = useState<ColDef[]>([
    { field: "placement", headerName: "Placement" },
    { field: "country", headerName: "Country" },
    { field: "revenue", headerName: "Revenue" },
    { field: "ecpm", headerName: "eCPM" },
    { field: "inv_available", headerName: "Inv. Available" },
    { field: "inv_booked", headerName: "Inv. Booked" },
    { field: "inv_unsold", headerName: "Inv. Unsold" },
    { field: "inv_remaining", headerName: "Inv. Remaining" },
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
          rowData={inventoryData || []}
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
