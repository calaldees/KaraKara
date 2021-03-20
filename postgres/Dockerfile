FROM postgres:13-alpine
EXPOSE 5432
VOLUME /var/lib/postgresql
HEALTHCHECK --interval=1m --timeout=5s CMD psql -U karakara karakara -c 'select 1'
COPY karakara.sql /docker-entrypoint-initdb.d/
