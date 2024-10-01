import {
  Drawer as MuiDrawer,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  Divider,
  ListItemText,
} from "@mui/material";
import { useNavigate } from "react-router";
import { styled } from "@mui/system";

interface LayoutDrawerProps {
  drawerWidth?: number;
  container?: any;
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
  selectedItem: number | null;
  setSelectedItem: (item: number | null) => void;
}

const drawerItems = [
  {
    name: "Campaign",
    path: "/campaign",
  },
];

const MobileDrawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "drawerWidth",
})<{ drawerWidth: number }>(({ drawerWidth, theme }) => ({
  "& .MuiDrawer-paper": {
    boxSizing: "border-box",
    width: drawerWidth,
  },
  display: "block",
  [theme.breakpoints.up("md")]: {
    display: "none",
  },
}));

const DesktopDrawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "drawerWidth",
})<{ drawerWidth: number }>(({ drawerWidth, theme }) => ({
  "& .MuiDrawer-paper": {
    boxSizing: "border-box",
    width: drawerWidth,
  },
  display: "none",
  [theme.breakpoints.up("md")]: {
    display: "block",
  },
}));

export default function LayoutDrawer({
  drawerWidth = 240,
  container,
  mobileOpen,
  handleDrawerToggle,
  selectedItem,
  setSelectedItem,
}: LayoutDrawerProps) {
  const navigate = useNavigate();

  const handleClick = (path: string) => {
    if (path) {
      navigate(path);
    }
    handleDrawerToggle();
  };

  const drawerContent = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        {drawerItems.map((item, index) => (
          <ListItem key={index} disablePadding>
            <ListItemButton
              selected={selectedItem === index}
              onClick={() => {
                setSelectedItem(index);
                handleClick(item.path);
              }}
            >
              <ListItemText primary={item.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <>
      <MobileDrawer
        container={container}
        variant="temporary"
        drawerWidth={drawerWidth}
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
      >
        {drawerContent}
      </MobileDrawer>
      <DesktopDrawer variant="permanent" drawerWidth={drawerWidth} open>
        {drawerContent}
      </DesktopDrawer>
    </>
  );
}
