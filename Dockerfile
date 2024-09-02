FROM docker.arvancloud.ir/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
#RUN pip install  -i http://185.128.40.208:8081/repository/parastaryab_group/ --trusted-host 185.128.40.208 --no-cache-dir -r requirements.txt
RUN pip install --trusted-host https://mirror-pypi.runflare.com -i https://mirror-pypi.runflare.com/simple/ -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
