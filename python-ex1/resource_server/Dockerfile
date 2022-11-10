# FROM python:3.10-alpine AS base

# RUN apk add build-base
# RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# ADD . /work
# WORKDIR /work

# RUN chown appuser:appgroup /work

# USER appuser
# RUN python -m venv .venv
# RUN source .venv/bin/activate
# RUN pip install -r requirements.txt

# ENTRYPOINT [ "python", "main.py" ]

FROM python:3.10-alpine AS base

ENV DB_USER=teste
ENV DB_PASSWORD=teste123
ENV DB_NAME=teste
ENV DB_PORT=3306
ENV DB_ADDRESS=postgresql

RUN apk add build-base linux-headers
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER root


FROM base as packages

RUN pip install --upgrade pip
ADD requirements.txt /work/requirements.txt
WORKDIR /work
RUN pip install -r requirements.txt


FROM packages as build

USER appuser
ADD . /work
WORKDIR /work


FROM build as test

CMD [ "pytest", "-s" ]


FROM build as run

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0"]