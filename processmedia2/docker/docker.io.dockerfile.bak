FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    docker.io \
&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt

# docker pull ubuntu:latest
# docker build -t docker.io:latest --file .\docker.io.dockerfile .
# docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock docker.io /bin/bash
    # Windows -v //var/run/docker.sock:/var/run/docker.sock
