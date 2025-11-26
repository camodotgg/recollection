# Frontend Dockerfile for TanStack Start application

FROM node:20-alpine AS base

# Install pnpm
RUN npm install -g pnpm@10.23.0

# Development stage
FROM base AS development

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["pnpm", "dev"]

# Production build stage
FROM base AS builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN pnpm build

# Production stage
FROM base AS production

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install production dependencies only
RUN pnpm install --prod --frozen-lockfile

# Copy built application
COPY --from=builder /app/.output ./.output

# Expose port
EXPOSE 3000

# Start production server
CMD ["pnpm", "serve"]
