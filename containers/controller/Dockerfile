FROM alpine:3.19

COPY src/requirements.txt /opt/requirements.txt

RUN apk update && \
    apk add --update --no-cache python3 py3-pip && \
    pip install pyclean --no-cache-dir && \
    pip install -r /opt/requirements.txt && \
    pyclean -v /usr && \
    pyclean -v ~/ && \
    pip uninstall -y pyclean && \
    rm -rf /var/cache/apk/* \



COPY src/ /opt/

ENTRYPOINT ["kopf run", "/opt/controller.py"]
#CMD ["--help"]
#ENV PATH "$PATH:/new/path"