FROM python:3.10-slim

WORKDIR /app

COPY discord_bot.py requirements.txt embeds.py /app/

RUN pip install -r requirements.txt

CMD ["python", "discord_bot.py"]