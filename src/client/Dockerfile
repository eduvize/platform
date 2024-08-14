# Stage 1: Build the React Vite app
FROM node:22 AS builder

# Set working directory
WORKDIR /app
ARG MODE=local

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React Vite app
RUN npm run build:${MODE}

# Stage 2: Serve the app with Nginx
FROM nginx:stable-alpine AS production

# Copy the built app from the builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Harden the Nginx container
RUN apk --no-cache add --virtual .build-deps curl bash \
    && apk --no-cache add --update \
    && rm -rf /var/cache/apk/* /tmp/* \
    && rm /etc/nginx/conf.d/default.conf \
    && rm -rf /var/lib/apt/lists/*

# Add a custom Nginx configuration
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Set the environment variable for PORT, default to 80
ENV PORT=80
ENV HOSTNAME=eduvize.dev

# Expose the port
EXPOSE $PORT

# Start Nginx with envsubst to replace the port in the template
CMD ["sh", "-c", "envsubst '${PORT} ${HOSTNAME}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
