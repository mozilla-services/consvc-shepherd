import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

export function createWrapper() {
  const testQueryClient = createTestQueryClient();
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <QueryClientProvider client={testQueryClient}>
      {children}
    </QueryClientProvider>
  );
  Wrapper.displayName = "QueryClientWrapper";
  return Wrapper;
}

export const TEST_URL = "http://localhost-test";
