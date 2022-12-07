FROM ghcr.io/julianfrattini/cira-dev:latest

WORKDIR /cira

# Install Python dependencies and setup cira version
COPY setup.py .
COPY README.md .
RUN pip3 install -e .

# Set DEV_CONTAINER to true such that the code references the models in the container
ENV DEV_CONTAINER=TRUE

COPY ./src ./src
COPY ./app.py ./app.py

CMD ["python", "app.py"]