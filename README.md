# 304bot

A Discord bot built with discord.py.

## Features

- Basic commands: `!ping`, `!hi`, `!kyle`, `!joshua`
- Member listing: `!members`
- Slash command: `/hi` with modal form interaction

## Setup

### Prerequisites

- Python 3.11+
- Discord Bot Token

### Environment Variables

Create a `.env` file in the root directory:

```
TOKEN=your_discord_bot_token_here
```

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the bot:
```bash
python main.py
```

## Docker

### Building the Docker Image

```bash
docker build -t 304bot .
```

### Running the Docker Container

```bash
docker run -e TOKEN=your_discord_bot_token_here 304bot
```

Or use a `.env` file:

```bash
docker run --env-file .env 304bot
```

### Docker Compose (Optional)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
```

Run with:

```bash
docker-compose up -d
```

## Configuration

- `TEST_GUILD_ID`: Set to your Discord server (guild) ID in `main.py`

## License

MIT
