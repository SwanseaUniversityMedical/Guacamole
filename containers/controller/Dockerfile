FROM alpine:3.19

COPY src/requirements.txt /opt/requirements.txt

RUN apk update && \
    apk add --update --no-cache python3 py3-pip && \
    pip install --break-system-packages pyclean --no-cache-dir && \
    pip install --break-system-packages -r /opt/requirements.txt && \
    pyclean -v /usr && \
    pyclean -v ~/ && \
    pip uninstall --break-system-packages -y pyclean && \
    rm -rf /var/cache/apk/* \

RUN pip install --break-system-packages -r /opt/requirements.txt

COPY src/ /opt/

ENTRYPOINT ["kopf run", "/opt/controller.py"]
#CMD ["--help"]
#ENV PATH "$PATH:/new/path"