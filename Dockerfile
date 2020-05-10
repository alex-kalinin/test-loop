FROM guyroyse/redismod
# FROM redislabs/redisedge:latest

RUN set -ex; \
    apt-get update; \
    apt-get install -y libgtk2.0-dev

