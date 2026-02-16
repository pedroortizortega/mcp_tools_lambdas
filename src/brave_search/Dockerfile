FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser
RUN playwright install chromium

# Copy application code
COPY . /app/

# Create __init__ for src package so imports work
RUN touch /app/src/__init__.py

ENV PYTHONPATH=/app
ENV BROWSER_HEADLESS=true
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["python", "-m", "src.browser.main"]
