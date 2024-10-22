
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig(({ mode }) => {
  // Load environment variables based on the mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [
      react(),
    ],
    server: {
      host: true,
      strictPort: true,
      port: 5173,
      watch: {
        usePolling: true,
      },
    },
    define: {
      'process.env': {
        NODE_ENV: JSON.stringify(env.VITE_NODE_ENV),
        SENTRY_DSN: JSON.stringify(env.VITE_SENTRY_DSN)

      },
    },
  };
});
