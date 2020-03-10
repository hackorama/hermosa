FROM python:3.7

ADD requirements.txt requirements.txt
ADD server.py server.py

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3","-u","server.py"]
