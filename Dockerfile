FROM node:22.12.0-alpine3.21 AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    TERRAFORM_VERSION=1.6.0 \
    CDKTF_VERSION=latest

RUN apk add --no-cache \
    python3 python3-dev py3-pip \
    gcc musl-dev linux-headers libffi-dev openssl-dev build-base \
    git curl jq unzip bash

RUN curl -fsSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform \
    && rm -f terraform.zip

RUN npm install -g cdktf-cli@$CDKTF_VERSION \
    && npm cache clean --force

RUN python3 -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install --upgrade pip \
    && $VIRTUAL_ENV/bin/pip install psutil requests azure-cli \
    && rm -rf ~/.cache/pip

FROM node:22.12.0-alpine3.21

ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/usr/local/bin:$PATH"

COPY --from=builder /usr/local/bin/terraform /usr/local/bin/terraform
COPY --from=builder /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=builder /opt/venv /opt/venv

RUN apk add --no-cache \
    python3 py3-pip curl git jq bash \
    && ln -s ../lib/node_modules/cdktf-cli/bundle/bin/cdktf /usr/local/bin/cdktf

WORKDIR /app

CMD ["bash"]
