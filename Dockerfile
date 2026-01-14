FROM mcr.microsoft.com/azure-cli:2.60.0

ARG TERRAFORM_VERSION=1.6.6

RUN apk add --no-cache curl unzip \
  && curl -fsSLo /tmp/terraform.zip "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
  && unzip /tmp/terraform.zip -d /usr/local/bin \
  && rm -f /tmp/terraform.zip

WORKDIR /workspace
ENTRYPOINT ["/bin/sh"]
