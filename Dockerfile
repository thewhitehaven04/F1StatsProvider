FROM python:3.11.10-slim-bookworm

RUN pip install poetry
COPY / . 
RUN poetry install 
WORKDIR /f1data
CMD ["poetry", "run", "hypercorn", "main:app", "--bind", "::"]