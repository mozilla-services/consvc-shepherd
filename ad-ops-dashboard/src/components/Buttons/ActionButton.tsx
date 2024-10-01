import { ReactNode } from "react";
import { IconButton } from "@mui/material";

interface ActionButtonProps {
  icon: ReactNode;
  handleClick: () => void;
}
export default function ActionButton({ icon, handleClick }: ActionButtonProps) {
  return <IconButton onClick={handleClick}>{icon}</IconButton>;
}
