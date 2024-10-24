import { useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef } from "ag-grid-community";
import { Box, Button } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import AppLoader from "../../components/AppLoader/AppLoader";
import ConfirmationDialog from "../../components/Dialogs/ConfirmationDialog";
import FormDialog from "../../components/Dialogs/FormDialog";
import CampaignForm from "../../components/Forms/CampaignForm";
import {
  CampaignFormSchema,
  defaultCampaignValues,
} from "../../utils/schemas/campaignFormSchema";
import {
  useDeleteCampaignMutation,
  useGetCampaignsQuery,
} from "../../data/campaigns";
import ActionButton from "../../components/Buttons/ActionButton";
import { styled } from "@mui/system";
import SplitCampaignForm from "../../components/Forms/SplitCampaignForm";
import { CallSplit } from "@mui/icons-material";

const ButtonContainer = styled(Box)`
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;

const TableContainer = styled(Box)`
  width: 100%;
  margin-top: 1rem;
`;

interface ActionButtonsComponentProps {
  handleCampaignDelete: () => void;
  handleCampaignEdit: () => void;
  handleSplitModal: () => void;
}

const ActionButtonsComponent = ({
  handleCampaignDelete,
  handleCampaignEdit,
  handleSplitModal,
}: ActionButtonsComponentProps) => {
  return (
    <Box>
      <ActionButton
        icon={<EditIcon aria-label="edit" color="primary" />}
        handleClick={handleCampaignEdit}
      />
      <ActionButton
        icon={<DeleteIcon aria-label="delete" color="error" />}
        handleClick={handleCampaignDelete}
      />
      <ActionButton handleClick={handleSplitModal} icon={<CallSplit />} />
    </Box>
  );
};

export default function Campaign() {
  const [isUpdate, setIsUpdate] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [openSplitCampaignModal, setOpenSplitCampaignModal] = useState(false);
  const [isConfirm, setIsConfirm] = useState(false);
  const [formData, setFormData] = useState<CampaignFormSchema>(
    defaultCampaignValues
  );

  const deleteCampaignMutation = useDeleteCampaignMutation();

  const handleOpen = () => {
    setIsUpdate(false);
    setOpenModal(true);
  };

  const handleClose = () => {
    setOpenModal(false);
    setFormData(defaultCampaignValues);
  };

  const {
    data: campaignsData,
    error,
    isPending,
    isFetching,
  } = useGetCampaignsQuery();
  const [colDefs] = useState<ColDef[]>([
    { field: "notes", headerName: "Notes" },
    { field: "ad_ops_person", headerName: "Ad Ops Person" },
    {
      headerName: "Kevel Flight IDs",
      valueGetter: (params: {
        data: { flights?: { kevel_flight_id: string }[] };
      }) =>
        params.data.flights
          ?.map((flight) => flight.kevel_flight_id)
          .join(", ") ?? "",
    },
    { field: "impressions_sold", headerName: "Impressions Sold" },
    { field: "net_spend", headerName: "Net Spend" },

    { field: "seller", headerName: "Seller" },
    {
      field: "button",
      headerName: "Actions",
      flex: 1,
      headerClass: "header-center",
      cellStyle: { textAlign: "center" },
      cellRenderer: (data: { data: CampaignFormSchema }) => (
        <ActionButtonsComponent
          handleCampaignEdit={() => {
            setIsUpdate(true);
            setFormData(data.data);
            setOpenModal(true);
          }}
          handleCampaignDelete={() => {
            setIsConfirm(true);
            setFormData(data.data);
          }}
          handleSplitModal={() => {
            setFormData(data.data);
            setOpenSplitCampaignModal(true);
          }}
        />
      ),
      filter: false,
    },
  ]);

  if (isPending || isFetching) return <AppLoader />;

  if (error) return "An error has occurred: " + error.message;

  const defaultColDef: ColDef = {
    flex: 1,
  };

  const handleCloseSplitFormDialog = () => {
    setOpenSplitCampaignModal(false);
    setFormData(defaultCampaignValues);
  };

  return (
    <>
      <ConfirmationDialog
        handleOk={() => {
          setIsConfirm(false);
          deleteCampaignMutation.mutate(formData.id);
          setFormData(defaultCampaignValues);
        }}
        message="Are you sure to delete campaign?"
        title="Delete Campaign"
        openConfirmation={isConfirm}
        handleClose={() => {
          setIsConfirm(false);
          setFormData(defaultCampaignValues);
        }}
      />

      <FormDialog
        title={isUpdate ? "Update Campaign" : "Add Campaign"}
        handleClose={handleClose}
        open={openModal}
      >
        <CampaignForm
          formData={formData}
          isUpdate={isUpdate}
          handleClose={handleClose}
          campaigns={campaignsData}
        />
      </FormDialog>

      <FormDialog
        title="Campaign Split Form"
        handleClose={() => {
          handleCloseSplitFormDialog();
        }}
        open={openSplitCampaignModal}
        maxWidth="xl"
      >
        <SplitCampaignForm
          formData={formData}
          handleClose={() => {
            handleCloseSplitFormDialog();
          }}
        />
      </FormDialog>

      <ButtonContainer>
        <Button onClick={handleOpen} variant="contained">
          Add Data
        </Button>
      </ButtonContainer>
      <TableContainer className="ag-theme-quartz">
        <AgGridReact
          rowData={campaignsData}
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
