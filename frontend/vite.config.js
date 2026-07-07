import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During local `npm run dev`, requests to /api are proxied to the backend so the
// frontend code can always talk to a stable "/api" base. In Docker, nginx does
// the same proxying (see nginx.conf).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
