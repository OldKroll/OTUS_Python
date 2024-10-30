
Запуск: 
```sh
# Для сборки контейнера
$ docker build . -t pb_c_ext 
# Для запуска контейнера
$ docker run --name docker_hw_pb -ti pb_c_ext /bin/bash 
#Запуск скрипта
$ python3 test.py
```
Настройка Dockerfile:
```Dockerfile
# для возможности интерактивного подключения
CMD /bin/sh -c "while sleep 1000; do :; done" 
# или для запуска теста
CMD python3 test.py
```
