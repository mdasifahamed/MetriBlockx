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
      script: "/root/MetriBlockx/metrics/venv/bin/python3",
      args: "-m metrics.startStream",
      interpreter: "none",
      instances: 1,
      cwd: "/root/MetriBlockx",
      autorestart: true,
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },

    // Polygon Worker
    {
      name: "worker-ethereum",
      script: "npx",
      args: "tsx src/index.ts --chain=ethereum --block=24422655 --targetBlock=24444137",
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
