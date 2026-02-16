FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync

COPY . .

CMD ["uv", "run", "python", "main.py"]
