FROM python:3.11-slim-bookworm

WORKDIR /app

# Install Playwright and its dependencies (chromium will be installed by playwright)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates fonts-liberation libnss3 libasound2 libatk-bridge2.0-0 libdbus-1-3 libdrm-dev libgbm-dev libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libx11-xcb1 libxcb-dri3-0 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 libxshmfence-dev libxss1 libxtst6 xdg-utils --fix-missing && rm -rf /var/lib/apt/lists/*

COPY agent.py .
COPY requirements.txt .

RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps

CMD ["python", "-u", "agent.py"]
