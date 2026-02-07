module.exports = {
  apps: [
    {
      name: "data-processors",
      script: "npx",
      args: "tsx src/startProcessors.ts",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "prod",
      },
    },

    // Ethereum Worker
    {
      name: "worker-ethereum",
      script: "npx",
      args: "tsx src/index.ts --chain=ethereum --block=23914924 --targetBlock=23964383",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "production",
      },
    },

    // Polygon Worker
    {
      name: "worker-polygon",
      script: "npx",
      args: "tsx src/index.ts --chain=polygon --block=70060972 --targetBlock=70866989",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "production",
      },
    },

    // BNB Worker
    {
      name: "worker-bnb",
      script: "npx",
      args: "tsx src/index.ts --chain=bnb --block=79762494 --targetBlock=80021678",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
