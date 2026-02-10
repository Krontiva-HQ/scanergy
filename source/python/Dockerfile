FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY simple_websocket_server.py /app/simple_websocket_server.py
EXPOSE 8765
CMD ["python", "/app/simple_websocket_server.py"]
