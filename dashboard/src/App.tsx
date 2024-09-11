import {
  useQuery,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { getProducts } from "./queries";

// Create a client
const queryClient = new QueryClient();

export default function App() {
  return (
    // Provide the client to your App
    <QueryClientProvider client={queryClient}>
      <Products />
    </QueryClientProvider>
  );
}

function Products() {
  const { isPending, error, data } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
  });

  if (isPending) return "Loading...";

  if (error) return "An error has occurred: " + error.message;

  return (
    <div className="Dashboard">
      <header className="Dashboard-header">
        <h1>Welcome to The Ad Ops Dashboard</h1>
      </header>
      <div>
        <h2>Boostr Products</h2>
        <ul>
          {data.map((p) => (
            <li
              key={p.name}
              style={{
                listStyleType: "none",
                padding: "10px",
                fontSize: "20px",
              }}
            >
              {p.name}, {p.country || "RON"}, {p.campaign_type || "None"}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
