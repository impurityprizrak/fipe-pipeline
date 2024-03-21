FROM python:3.11

RUN python -m pip install --upgrade pip setuptools

RUN python -m pip install virtualenv
RUN virtualenv /env -p python3.11

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
ENV APP_HOME /app
ENV PORT 5000

WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD python main.py