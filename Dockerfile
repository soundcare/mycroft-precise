FROM python:3.7-slim-buster
COPY ./ /
WORKDIR /
RUN apt-get update && apt-get install -y build-essential git \
    python3-dev \
    cython3
RUN ./setup-docker.sh
CMD /bin/bash
