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

Create a `.env` file in the root directory (this file should NOT be committed to git or included in the Docker image):

```
TOKEN=your_discord_bot_token_here
```

**Note**: The `.env` file is excluded from the Docker image via `.dockerignore` for security. You'll pass environment variables at runtime using `-e` or `--env-file` flags.

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
services:
  bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
```

Run with:

```bash
docker compose up -d
```

## Configuration

- `TEST_GUILD_ID`: Currently hardcoded in `main.py` (line 11). To use this bot in your server, update this value to your Discord server (guild) ID.
- `TOKEN`: Discord bot token, passed via environment variable (required)

## License

MIT
