FROM python:alpine3.7 
COPY . /app
WORKDIR /app/kochi
RUN pip install -r requirements.txt 
EXPOSE 5000
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ] 
