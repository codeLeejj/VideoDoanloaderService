FROM python:3.10-slim

WORKDIR /app

# copy coding files
COPY requirements.txt .
COPY app.py .
COPY AddressHandler.py .

# copy web files
COPY /templates/index.html ./templates/

COPY /bin/ffmpeg ../usr/bin/ffmpeg
#COPY /bin/ffprobe ../usr/bin/ffprobe
#COPY /bin/ffplay ../usr/bin/ffplay


RUN pip install --no-cache-dir -r requirements.txt
RUN pip install ffmpeg

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]