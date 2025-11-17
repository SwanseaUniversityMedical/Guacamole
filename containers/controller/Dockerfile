FROM alpine:3.19

COPY src/requirements.txt /opt/requirements.txt

RUN apk update && \
    apk add --update --no-cache python3 py3-pip && \
    pip install --break-system-packages pyclean --no-cache-dir && \
    pip install --break-system-packages -r /opt/requirements.txt && \
    pyclean -v /usr && \
    pyclean -v ~/ && \
    pip uninstall --break-system-packages -y pyclean && \
    rm -rf /var/cache/apk/*

RUN adduser -D -u 1001 -g 1001 controller

COPY src/ /opt/

# Run as the non-root user
USER 1001

ENTRYPOINT ["kopf", "run", "-A", "/opt/controller.py"]
#CMD ["--help"]
#ENV PATH "$PATH:/new/path"
