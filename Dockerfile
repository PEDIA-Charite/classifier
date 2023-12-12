FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py ./main.py
COPY pedia.py ./pedia.py

COPY lib ./lib
COPY train ./train
RUN mkdir -p ./input
RUN mkdir -p ./output


CMD [ "uvicorn",  "main:app", "--host", "0.0.0.0", "--port", "9000" ]
