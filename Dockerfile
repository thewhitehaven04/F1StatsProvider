FROM python:3.11.10-slim-bookworm

RUN pip install poetry
COPY /pyproject.toml .
COPY /poetry.lock .
COPY ./f1data /f1data
RUN poetry install 
COPY . . 
WORKDIR /f1data
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]