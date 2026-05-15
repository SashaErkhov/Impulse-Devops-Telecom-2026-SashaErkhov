FROM python:3.12.3-slim
COPY . /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt-get update && \
  apt-get install -y wget curl nano
RUN wget https://example.com/some-tool.tar.gz && \
  tar -xzf some-tool.tar.gz && \
  mv some-tool /usr/local/bin/ && \
  rm some-tool.tar.gz
CMD ["python", "/app/src/app.py"]