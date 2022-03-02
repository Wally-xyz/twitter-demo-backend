FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
ENV AWS_DEFAULT_REGION='us-east-1'
# DD_PROFILING_ENABLED=true

RUN apt-get -y update && apt-get -y upgrade
CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "80"]

# Gunicorn for production to scale workers

# CMD ["ddtrace-run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "app.src.main:app", "--bind", "0.0.0.0:80"]


# To run this locally via docker:
# docker run -v $HOME/.aws/credentials:/root/.aws/credentials:ro -d --name mycontainer23 -p 80:80 myimage_gunicorn