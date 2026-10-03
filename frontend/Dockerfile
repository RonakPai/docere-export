FROM node:16

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your application files
COPY . .

# Run the build command for your application
# RUN npm run build

# Expose the port your Express app runs on
EXPOSE 3000

# Start the server (assuming your Express entry point is index.js)
# CMD ["node", "index.js"]
CMD ["npm", "start"]