FROM python:3.12-slim

WORKDIR /app
COPY bot.py .

RUN pip install --no-cache-dir discord.py aiohttp

CMD ["python", "bot.py"]
