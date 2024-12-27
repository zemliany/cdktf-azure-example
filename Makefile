
IMAGE ?= zemlyanoy/cdktf-python-azure
HOST_AZURE_CREDS ?= $(HOME)/.azure.docker.tmp/
CDKTF_AZURE_CREDS ?= /home/cdktf/.azure

.PHONY: apply destroy plan build help

check-email:
	@if [ -z "$(EMAIL)" ]; then \
		echo "Error: EMAIL argument is required. Use 'make plan EMAIL=myemail@setuniversity.edu.ua'."; \
		exit 1; \
	fi

check-tag:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG argument is required. Use 'make build TAG=0.3"; \
		exit 1; \
	fi

check-docker:
	@docker info > /dev/null 2>&1 || (echo "Error: Docker is not installed, not running, or you do not have sufficient permissions. Please ensure Docker is installed, running, and accessible." && exit 1)

apply: check-docker
	@echo "Running 'apply' CDKTF Azure stack..."
	docker run --rm -v $(HOST_AZURE_CREDS):$(CDKTF_AZURE_CREDS) $(IMAGE) apply $(EMAIL)

destroy: check-docker
	@echo "Running 'destroy' CDKTF Azure stack..."
	docker run --rm -v $(HOST_AZURE_CREDS):$(CDKTF_AZURE_CREDS) $(IMAGE) destroy $(EMAIL)

plan: check-docker
	@echo "Running 'plan' CDKTF Azure stack..."
	docker run --rm -v $(HOST_AZURE_CREDS):$(CDKTF_AZURE_CREDS) $(IMAGE) plan $(EMAIL)


build: check-docker check-tag
	@echo "Building Docker image $(IMAGE) with $(TAG)..."
	docker buildx build --no-cache --provenance=false --platform linux/amd64,linux/arm64 -t $(IMAGE):$(TAG) .


help:
	@echo "Available targets:"
	@echo "  apply          - Apply infrastructure with your email"
	@echo "  destroy        - Destroy infrastructure with your email"
	@echo "  plan           - Plan infrastructure changes with your email"
	@echo "  build          - Build the Docker image"
	@echo "  help           - Show this help message"
