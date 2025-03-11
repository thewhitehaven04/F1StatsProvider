FROM python:3.11.11-alpine3.21

RUN pip install poetry
COPY / . 
RUN poetry install 
WORKDIR /f1data
CMD ["poetry", "run", "hypercorn", "main:app", "--bind", "::"]