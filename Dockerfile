FROM python:3.6-alpine
ARG BIN_VERSION=<unknown>

RUN mkdir /app
COPY ./*.py ./requirements.txt /app/
WORKDIR /app
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apk del .build-deps
ENTRYPOINT ["python", "/app/instapaper_archiver.py"]

LABEL license="MIT"
LABEL maintainer="Chris Dzombak <https://www.dzombak.com>"
LABEL org.opencontainers.image.authors="Chris Dzombak <https://www.dzombak.com>"
LABEL org.opencontainers.image.url="https://github.com/cdzombak/instapaper-auto-archiver"
LABEL org.opencontainers.image.documentation="https://github.com/cdzombak/instapaper-auto-archiver/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/cdzombak/instapaper-auto-archiver.git"
LABEL org.opencontainers.image.version="${BIN_VERSION}"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="instapaper-auto-archiver"
LABEL org.opencontainers.image.description="Automatically archive older unread Instapaper bookmarks"
