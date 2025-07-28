FROM node:20.12.2

WORKDIR /app
COPY . .

RUN npm install

# Expose port 5173 for Vite dev server
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]