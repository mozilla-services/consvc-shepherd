# Dev Dockerfile
FROM node:20.17.0-slim

WORKDIR /ad-ops-dashboard

COPY package*.json .

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
