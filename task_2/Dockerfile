FROM python:3.11-slim-bullseye
COPY .  /usr/src/app/
WORKDIR /usr/src/app/
RUN apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt

ENV FLASK_APP=app.py

ENV FLASK_DEBUG=true
ENV FLASK_ENV=development

ENTRYPOINT ["python"]
CMD ["app.py"]