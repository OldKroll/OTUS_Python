FROM python:3.12

WORKDIR /proj

COPY ./mysite/ .

RUN groupadd -g 1000 user && \
    useradd -m -u 1000 -g user user && \
    chown -R user:user /proj 

USER user:user

RUN pip3 install django gunicorn psycopg2 && \
    echo "yes" | python3 manage.py collectstatic

