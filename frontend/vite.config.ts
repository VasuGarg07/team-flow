import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

const backendUrl = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [tailwindcss()],
  resolve: {
    alias: { "@": "/src" },
  },
  server: {
    port: 5173,
    proxy: {
      "/auth": backendUrl,
      "/users": backendUrl,
      "/health": backendUrl,
    },
  },
});
