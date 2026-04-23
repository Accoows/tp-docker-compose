FROM mongodb/mongodb-community-server:8.0-ubi8

USER root

RUN mkdir -p /data/db && chown -R 1001:0 /data/db

COPY --chown=1001:0 db.js /docker-entrypoint-initdb.d/

USER 1001

EXPOSE 27017