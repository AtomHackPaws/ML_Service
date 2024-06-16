FROM python:3

RUN apt-get update && apt-get install software-properties-common -y --no-install-recommends

RUN apt-get install -y --no-install-recommends \
        locales \
        tzdata \
        openssh-client \
        nano \
        wget

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN pip3 install --upgrade pip setuptools

COPY requirements.txt .
RUN for req in $(cat requirements.txt); do pip3 install $req; done
RUN rm requirements.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY . .

CMD faststream run app.main:app