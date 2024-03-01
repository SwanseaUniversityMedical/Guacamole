FROM alpine:3.19 as base

COPY src/requirements.txt /opt/requirements.txt

RUN apk update && \
    apk add --update --no-cache python3 py3-pip && \
    pip install --break-system-packages pyclean --no-cache-dir && \
    pip install --break-system-packages -r /opt/requirements.txt --no-cache-dir && \
    pyclean -v /usr && \
    pyclean -v ~/ && \
    pip uninstall --break-system-packages -y pyclean && \
    apk del py3-pip && \
    rm -rf /var/cache/apk/*

COPY src/ /opt/

ENTRYPOINT ["python3", "/opt/controller.py"]
#CMD ["--help"]
