FROM python:3.15-slim
WORKDIR /app
COPY app ./app
EXPOSE 8080
USER 65532:65532
CMD ["python", "-m", "app.server"]
