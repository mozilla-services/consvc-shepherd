import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "./static", // matches STATIC_URL in settings.py
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
  },
});
