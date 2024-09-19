import { Box, List, ListItem, ListItemText, Typography } from "@mui/material";
import { useGetProductsQuery } from "../../data/products";
import { Product } from "../../types";

function Products() {
  const { isPending, error, data } = useGetProductsQuery();

  if (isPending) return "Loading...";

  if (error) return "An error has occurred: " + error.message;

  return (
    <Box>
      <Typography variant="h2">Welcome to The Ad Ops Dashboard</Typography>
      <Box>
        <Typography variant="h3">Boostr Products</Typography>
        <List>
          {data.map((p: Product) => (
            <ListItem key={p.full_name}>
              <ListItemText>
                {p.full_name}, {p.country || "RON"}, {p.campaign_type || "None"}
              </ListItemText>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
}

export default function Dashboard() {
  return <Products />;
}
