import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/system";

interface ConfirmationDialogProps {
  openConfirmation: boolean;
  handleClose: () => void;
  handleOk: () => void;
  message: string;
  title?: string;
}

const StyledDeleteButton = styled(Button)(() => ({
  backgroundColor: "#bb060c",
  "&:hover": {
    backgroundColor: "#a50c0f",
  },
}));

export default function ConfirmationDialog({
  openConfirmation,
  handleClose,
  handleOk,
  message,
  title,
}: ConfirmationDialogProps) {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down("lg"));

  return (
    <Dialog
      fullScreen={fullScreen}
      open={openConfirmation}
      onClose={handleClose}
      aria-labelledby="responsive-dialog-title"
    >
      <DialogTitle id="responsive-dialog-title">{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button autoFocus onClick={handleClose} variant="outlined">
          Cancel
        </Button>
        <StyledDeleteButton onClick={handleOk} autoFocus variant="contained">
          Delete
        </StyledDeleteButton>
      </DialogActions>
    </Dialog>
  );
}
