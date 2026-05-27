FROM node:20-alpine AS base
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@10.11.0 --activate

FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["pnpm", "dev"]

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time public URLs are baked into the client bundle (SSE/API base URLs).
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_BUILD_SHA
ARG NEXT_PUBLIC_BUILD_TIME
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_BUILD_SHA=${NEXT_PUBLIC_BUILD_SHA}
ENV NEXT_PUBLIC_BUILD_TIME=${NEXT_PUBLIC_BUILD_TIME}

RUN pnpm build

FROM node:20-alpine AS production
WORKDIR /app

# Next standalone server output.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
