import { ReactNode } from "react";
import {
  Box,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from "@mui/material";

import { styled } from "@mui/system";

import { Close } from "@mui/icons-material";
import ActionButton from "../Buttons/ActionButton";

interface FormDialogProps {
  title?: string;
  actions?: ReactNode;
  children: ReactNode;
  open: boolean;
  handleClose: () => void;
}

const Container = styled(Box)`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export default function FormDialog({
  title,
  actions,
  children,
  open,
  handleClose,
}: FormDialogProps) {
  return (
    <Dialog
      fullWidth
      scroll="paper"
      open={open}
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
      aria-modal
    >
      <DialogTitle>
        <Container>
          <Typography>{title}</Typography>
          <ActionButton handleClick={handleClose} icon={<Close />} />
        </Container>
      </DialogTitle>

      <DialogContent>{children}</DialogContent>
      <DialogActions>{actions}</DialogActions>
    </Dialog>
  );
}
