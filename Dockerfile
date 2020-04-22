#publicly available docker image "python" on docker hub will be pulled

FROM python:3.7.6

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY hex /hex
COPY libs /libs
CMD python hex/run.py