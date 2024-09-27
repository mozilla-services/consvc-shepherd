FROM node:alpine

WORKDIR /ad-ops-dashboard

COPY package*.json .

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
