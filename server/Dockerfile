FROM python:2

ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y xfonts-75dpi
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xf  wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN cd ./wkhtmltox
RUN cp -R ./* /usr/
RUN cd
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
