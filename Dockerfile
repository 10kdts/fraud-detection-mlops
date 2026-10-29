FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN python -m src.fraudml.generate && python -m src.fraudml.model
EXPOSE 8080
CMD ["python", "-m", "src.fraudml.api"]

