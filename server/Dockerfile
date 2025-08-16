FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-mysql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git --version

COPY pyproject.toml uv.lock ./

RUN pip install uv

ENV PATH="/usr/bin:$PATH"

RUN uv sync

COPY . .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
