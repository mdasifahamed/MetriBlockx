module.exports = {
  apps: [
    {
      name: "event-data-processors",
      script: "npx",
      args: "tsx src/startProcessors.ts",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "prod",
      },
    },

    // Python Stream Receiver
    {
      name: "metrics-genartor",
      script: "python3",
      args: "-m metrics.startStream",
      interpreter: "none",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },

    // Ethereum Worker
    {
      name: "worker-ethereum",
      script: "npx",
      args: "tsx src/index.ts --chain=ethereum --block=24461175 --targetBlock=24461205",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "production",
      },
    },

    {
      name: "worker-polygon",
      script: "npx",
      args: "tsx src/index.ts --chain=polygon --block=83019390 --targetBlock=83019450",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
