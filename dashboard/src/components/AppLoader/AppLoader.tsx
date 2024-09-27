import { Backdrop, Box, CircularProgress } from "@mui/material";
import { styled } from "@mui/system";

const StyledContainer = styled(Box)`
  display: flex;
  justify-content: flex-center;
  align-items: center;
`;

export default function AppLoader() {
  return (
    <StyledContainer>
      <Backdrop
        sx={(theme) => ({ color: "#fff", zIndex: theme.zIndex.drawer + 1 })}
        open={true}
      >
        <CircularProgress color="inherit" />
      </Backdrop>
    </StyledContainer>
  );
}
