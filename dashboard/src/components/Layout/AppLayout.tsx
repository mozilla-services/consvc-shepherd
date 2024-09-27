import { useState } from "react";
import {
  Typography,
  CssBaseline,
  Box,
  IconButton,
  AppBar,
  Toolbar,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import LayoutDrawer from "./LayoutDrawer";
import { useNavigate } from "react-router";
import { Outlet } from "react-router-dom";
import { styled } from "@mui/system";
const drawerWidth = 240;

interface LayoutProps {
  window?: () => Window;
}

const LayoutContainer = styled(Box)`
  display: flex;
`;

const StyledTypography = styled(Typography)<{ component?: React.ElementType }>(
  () => ({
    cursor: "pointer",
  })
);

const StyledIconButton = styled(IconButton)(({ theme }) => ({
  marginRight: theme.spacing(2),
  display: "block",
  [theme.breakpoints.up("md")]: {
    display: "none",
  },
}));

const StyledNavBox = styled(Box)(({ theme }) => ({
  width: "auto",
  flexShrink: 1,
  [theme.breakpoints.up("md")]: {
    width: drawerWidth,
    flexShrink: 0,
  },
}));

const StyledMainBox = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  width: "auto",
  [theme.breakpoints.up("md")]: {
    width: `calc(100% - ${drawerWidth}px)`,
  },
}));

export default function Layout({ window }: LayoutProps) {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<number | null>(0);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const container =
    window !== undefined ? () => window().document.body : undefined;

  return (
    <LayoutContainer>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <StyledIconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
          >
            <MenuIcon />
          </StyledIconButton>
          <StyledTypography
            variant="h6"
            onClick={() => {
              navigate("/"), setSelectedItem(null);
            }}
            noWrap
            component="header"
          >
            Ads Ops
          </StyledTypography>
        </Toolbar>
      </AppBar>
      <StyledNavBox>
        <LayoutDrawer
          drawerWidth={drawerWidth}
          handleDrawerToggle={handleDrawerToggle}
          mobileOpen={mobileOpen}
          container={container}
          setSelectedItem={setSelectedItem}
          selectedItem={selectedItem}
        />
      </StyledNavBox>
      <StyledMainBox>
        <Toolbar />

        <Outlet />
      </StyledMainBox>
    </LayoutContainer>
  );
}
