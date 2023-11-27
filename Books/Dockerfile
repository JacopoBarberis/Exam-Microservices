FROM python:3.11
WORKDIR /

COPY . . 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]