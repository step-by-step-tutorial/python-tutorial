FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential curl && apt-get clean
RUN python -m pip install --upgrade pip && pip install --no-cache-dir notebook jupyterlab pandas numpy matplotlib scikit-learn

ENV PORT=8888

EXPOSE $PORT

CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=$PORT --no-browser --allow-root --NotebookApp.token=''"]