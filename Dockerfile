FROM mcr.microsoft.com/azure-cli@sha256:6d7791e595999664478813ee6da9b340dc087be87cce9f581ded83cc4bf15ca0 AS azure-cli

FROM python:3.12-slim-bookworm

ENV TERRAFORM_VERSION=1.7.5 \
    CDKTF_VERSION=0.20.10

RUN apt-get clean && apt-get update && apt-get -qy upgrade \
    && apt-get -qy install vim jq curl unzip git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform \
    && rm -f terraform.zip

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install --global cdktf-cli@${CDKTF_VERSION} \
    && npm install --global yarn \
    && npm cache clean --force \
    && pip3 install pipenv

# Copy Azure CLI binary and dependencies from azure-cli
COPY --from=azure-cli /bin/az /usr/local/bin/az
COPY --from=azure-cli /usr/lib/az/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

RUN groupadd --gid 1001 cdktf \
    && useradd --uid 1001 --gid cdktf --create-home cdktf

WORKDIR /app
COPY entrypoint.sh /app
RUN chown -R cdktf:cdktf /app \
    && chmod +x /app/entrypoint.sh

USER cdktf

CMD [ "/app/entrypoint.sh" ]