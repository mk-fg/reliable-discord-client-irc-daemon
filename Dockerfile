ARG ALPINE_TAG=3.23
FROM alpine:${ALPINE_TAG}

LABEL \
	org.opencontainers.image.title="rdircd" \
	org.opencontainers.image.description="Reliable Discord-client IRC Daemon" \
	org.opencontainers.image.licenses="WTFPL" \
	org.opencontainers.image.url="https://github.com/mk-fg/reliable-discord-client-irc-daemon"

RUN apk add --no-cache python3 py3-aiohttp openssl

# See README.docker-permissions.md doc for a common "Permission denied" issue due to these
ARG UID=55373
ARG GID=55373

RUN echo "### Using following uid:gid for rdircd: $UID:$GID" && \
	addgroup -S -g $GID rdircd && adduser -S -h /config -s /bin/false -G rdircd -DH -u $UID rdircd
COPY rdircd rdircd.unicode-emojis.txt.gz /

USER rdircd:rdircd
ENV PYTHONUNBUFFERED=1
EXPOSE 6667
VOLUME /config
WORKDIR /config

ENTRYPOINT [ "/rdircd", "--conf", "config.ini", "-i", "0.0.0.0" ]
