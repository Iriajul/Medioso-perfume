###############################################################################
# Mad Perfume frontend (admin dashboard) — multi-stage image (Next.js, Node 20).
#
# Stages:
#   deps    — installs node_modules from the lockfile (cached on lockfile changes)
#   dev     — hot-reloading `next dev`, source bind-mounted by compose
#   builder — `next build` with output: "standalone"
#   prod    — minimal, non-root, runs the standalone server.js
#
#   docker build --target prod -t madperfume-frontend:prod .
#   docker build --target dev  -t madperfume-frontend:dev  .
###############################################################################

ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1


FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci


FROM deps AS dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]


FROM deps AS builder
# NEXT_PUBLIC_* values are inlined into the client bundle at build time.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY . .
RUN npm run build


FROM base AS prod
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000

COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "server.js"]
