# Stage 1: Build
FROM node:12.18-alpine AS builder

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH

COPY package.json ./
COPY package-lock.json ./
RUN npm install --unsafe-perm=true --allow-root

COPY . ./
RUN npm run build

# Stage 2: Production
FROM node:12.18-alpine

WORKDIR /app
RUN npm install -g serve

COPY --from=builder /app/build ./build

RUN chown -R 1000:0 /app && chmod -R ug+rwx /app
USER 1000

CMD ["serve", "-s", "build", "-l", "3000"]
