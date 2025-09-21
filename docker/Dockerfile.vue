FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json for Vue
COPY docker/package-vue.json /app/package.json

# Install dependencies
RUN npm install

# Copy Vue server
COPY docker/vue-server.js /app/

# Expose port 3000
EXPOSE 3000

# Start the development server
CMD ["node", "vue-server.js"]
