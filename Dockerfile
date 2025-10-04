FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY requirements.txt requirements_test.txt ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./app ./app
COPY ./routes ./routes

CMD ["app.main.handler"]