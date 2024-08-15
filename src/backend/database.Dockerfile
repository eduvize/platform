# Use the official Postgres image as the base
FROM postgres:13

# Set the working directory to the Postgres initialization directory
WORKDIR /docker-entrypoint-initdb.d/

# Copy your SQL script into the container
COPY scripts/database/seed_dev_environment.sql /docker-entrypoint-initdb.d/

# Expose the Postgres port
EXPOSE 5432