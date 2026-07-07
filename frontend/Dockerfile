# --- Build stage: compile the React app with Vite ----------------------
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first for better layer caching.
# package*.json matches package.json (and package-lock.json if present).
COPY package*.json ./
RUN npm install

# Build the production bundle.
COPY . .
RUN npm run build

# --- Serve stage: nginx serves the static files and proxies the API ----
FROM nginx:1.27-alpine

# Custom config: serve the SPA and forward /api to the backend container.
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
