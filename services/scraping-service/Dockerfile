FROM python:3.13-alpine

WORKDIR /app

# Install ChromeDriver, chromium for selenium
RUN apk add --no-cache chromium chromium-chromedriver

# copy the requirements.txt file
COPY requirements.txt /app/requirements.txt

# downlaod all dependencies for the project
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--log-level", "debug"]
