FROM python:3.15-slim
WORKDIR /app
COPY app ./app
COPY index.html ./index.html
RUN mkdir -p /data && chown 65532:65532 /data
EXPOSE 8080
USER 65532:65532
CMD ["python", "-m", "app.server"]
