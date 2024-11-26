SERVER_IMAGE=dagster-web-ui-new
SNOWFLAKE_REPO?=orgname-account.registry.snowflakecomputing.com/dagsterdb/public/images
IMAGE_REGISTRY=orgname-account.registry.snowflakecomputing.com
LOGIN_NAME=username

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

all: login build push

login:  ## Login to Snowflake Docker repo. Uses snowcli.
	docker login ${IMAGE_REGISTRY} -u $(LOGIN_NAME)

build: build_server #build_agent 

build_server: ## Builds dagster server image
	docker build --no-cache --platform linux/amd64 -t $(SERVER_IMAGE) . 

push: push_server 

push_server:
	docker tag $(SERVER_IMAGE) ${SNOWFLAKE_REPO}/$(SERVER_IMAGE)
	docker push ${SNOWFLAKE_REPO}/$(SERVER_IMAGE)

