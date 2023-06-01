# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

# use this path as default location for all subsequent commands
WORKDIR /app
# copy requirements from WORKDIR into image
COPY requirements.txt requirements.txt
# install modules into image
RUN pip3 install -r requirements.txt
# add source code (all other files from WORKDIR) into image
COPY . .
# tell Docker to run flask specifying an externally visible connection
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]
