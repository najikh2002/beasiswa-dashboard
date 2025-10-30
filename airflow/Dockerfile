FROM apache/airflow:2.7.1-python3.9

USER root
RUN apt-get update && apt-get install -y gcc python3-dev

USER airflow
RUN pip install --no-cache-dir \
    pandas \
    requests \
    beautifulsoup4 \
    lxml

COPY --chown=airflow:root init_airflow.sh /init_airflow.sh
RUN chmod +x /init_airflow.sh

ENTRYPOINT ["/init_airflow.sh"]