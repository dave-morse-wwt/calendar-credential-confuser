FROM python:3.13.3-slim
RUN pip install uv
COPY pyproject.toml uv.lock /app/
WORKDIR /app
RUN uv export --no-dev | uv pip install --system --requirements -
ENV PYTHONPATH="/app/src"
COPY ./src /app/src
EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]
