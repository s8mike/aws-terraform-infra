# Frontend image. Stage 1 builds the React app with Node; stage 2 serves the built files with nginx.

# ---- Stage 1: build the site ----
FROM node:22-alpine AS build
WORKDIR /app

# Install packages first, so Docker can reuse this layer when only source files change.
COPY package.json package-lock.json ./
RUN npm ci

# Copy the source and build into /app/dist (this type-checks everything first).
COPY . .
RUN npm run build

# ---- Stage 2: serve the built files ----
# The "unprivileged" nginx image runs as a normal user (not root) and listens on port 8080.
FROM nginxinc/nginx-unprivileged:stable-alpine

# Apply the operating system's available security fixes. This needs root, so the image switches to root for this
# one step and back to the unprivileged user below. Rebuild with --no-cache to refresh the fixes.
USER root
RUN apk upgrade --no-cache

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# The unprivileged nginx image already runs as user 101; saying so explicitly lets scanners and policies verify it.
# This must be the LAST user instruction: the container runs as whoever is named last.
USER 101
EXPOSE 8080