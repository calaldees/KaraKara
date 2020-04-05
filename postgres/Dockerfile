FROM postgres:9-alpine
EXPOSE 5432
VOLUME /logs
VOLUME /var/lib/postgresql
HEALTHCHECK --interval=1m --timeout=5s CMD psql -U karakara karakara -c 'select 1'

COPY karakara.sql /docker-entrypoint-initdb.d/
