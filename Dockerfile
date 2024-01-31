FROM python:3.12-alpine3.19

COPY src /code
WORKDIR /code

RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install -e .

ENV PYTHONPATH=/code/src

CMD ["uvicorn", "src.app:main", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
