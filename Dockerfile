FROM alpine:3.7

RUN apk add --no-cache openssh-client python3 py3-pip
RUN pip3 install flask

COPY ./app.py /app/

CMD python3 /app/app.py