FROM ubuntu:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc protobuf-c-compiler libprotobuf-c-dev zlib1g-dev \
    python3 python3-dev python3-setuptools nano

WORKDIR /app
COPY . .

RUN protoc-c --c_out=. deviceapps.proto
RUN python3 setup.py build
RUN python3 setup.py install

# для возможности интерактивного подключения
 CMD /bin/sh -c "while sleep 1000; do :; done" 
# или для запуска теста
# CMD python3 test.py