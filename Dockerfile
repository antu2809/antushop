FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip setuptools && pip install -r requirements.txt

COPY . /code/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "antushop.wsgi:application"]
