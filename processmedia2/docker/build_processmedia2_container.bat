SET PATH_BUILD=..
docker pull ubuntu:latest
docker build -t docker.io:latest --file .\docker.io.dockerfile .
docker build -t karakara/processmedia2_base:latest --file .\processmedia2.base.dockerfile .
docker build -t karakara/processmedia2:latest --file .\processmedia2.production.dockerfile %PATH_BUILD%
REM docker push karakara/processmedia2:latest
