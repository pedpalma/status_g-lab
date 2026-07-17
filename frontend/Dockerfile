# Imagem de desenvolvimento do frontend.
# Otimizada para hot reload via docker-compose.
# TODO: quando houver necessidade de deploy de produção, avaliar build multi-stage separado.

FROM node:24-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
