FROM alpine:3.21


RUN apk update
RUN apk add python3
RUN apk add py3-pip
WORKDIR /app
COPY /app /app
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages


EXPOSE 5555
CMD ["python3", "app.py"]