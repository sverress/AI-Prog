#publicly available docker image "python" on docker hub will be pulled

FROM python:3.7.6

COPY requirements.txt /

RUN pip install -r requirements.txt

#copying helloworld.py from local directory to container's helloworld folder

COPY hex /hex
COPY libs /libs

#running helloworld.py in container

CMD python hex/run.py