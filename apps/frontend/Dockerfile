FROM node:22-slim

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

ENV NODE_ENV=production

CMD ["sh", "-c", "pnpm start -- -H 0.0.0.0 -p ${PORT:-3000}"]
