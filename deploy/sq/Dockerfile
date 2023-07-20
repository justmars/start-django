# syntax=docker/dockerfile:1.2
FROM python:3.11-slim-bullseye AS builder
RUN apt update \
  && apt install -y build-essential wget pkg-config \
  && apt clean

ARG sqlite_year=2023
ARG sqlite_ver=3420000
RUN wget https://www.sqlite.org/$sqlite_year/sqlite-autoconf-$sqlite_ver.tar.gz \
  && tar xzf sqlite-autoconf-$sqlite_ver.tar.gz && rm sqlite-autoconf-$sqlite_ver.tar.gz \
  && ./sqlite-autoconf-$sqlite_ver/configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_JSON1" \
  && make && make install

ARG litestream_ver=0.3.9
RUN wget https://github.com/benbjohnson/litestream/releases/download/v$litestream_ver/litestream-v$litestream_ver-linux-amd64-static.tar.gz \
  && tar xzf litestream-v$litestream_ver-linux-amd64-static.tar.gz && rm litestream-v$litestream_ver-linux-amd64-static.tar.gz \
  && mv litestream /usr/local/bin

FROM python:3.11-slim-bullseye
COPY --from=builder /usr/local/lib/ /usr/local/lib/
COPY --from=builder /usr/local/bin /usr/local/bin
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LD_LIBRARY_PATH=/usr/local/lib
ARG run_cmd
WORKDIR /opt/src
COPY /src .
RUN pip install -r requirements.txt \
  && chmod +x /opt/src/scripts/worker.sh /opt/src/scripts/$run_cmd
