# Dagster-in-snowpark-container-services
Orchestrating and Running your Data pipelines using Dagster in Snowpark Container Service

In order to run the dagtser in the container on your local machine, we need to set some environment variables in our terminal session before running the container. The variables to set are:

SNOWFLAKE_ACCOUNT - the account locator for the Snowflake account
SNOWFLAKE_USER - the Snowflake username to use
SNOWFLAKE_PASSWORD - the password for the Snowflake user
SNOWFLAKE_WAREHOUSE - the warehouse to use
SNOWFLAKE_DATABASE - the database to set as the current database (does not really matter that much what this is set to)
SNOWFLAKE_SCHEMA - the schema in the database to set as the current schema (does not really matter that much what this is set to)
SNOWFLAKE_ROLE - the role which has access to the DB

Once the environmental variables are set go to the dagster-spcs folder and make changes to the orgname-account name and also change the login name run the following command.

```bash 
make build
```

For local testing bring up the containers on your local machine by running the below.
```bash
docker compose up
```

Launch the dagter UI and once your testing is done bring down the containers by running the below command.
```bash
docker compose down
```


## Prerequisites

- Docker installed on your local machine (for building the custom image)
- Snowflake non-trail account
- Complete the following tutorial as that will be used in the assets.

https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials/tutorial-2


## Steps to Deploy 

Download and unzip the repo and you find a Readme.md and dagster-spcs folder which has all the code required.

### 1. Setup

``` sql
USE ROLE ACCOUNTADMIN;

CREATE ROLE DAGSTER_ROLE;

CREATE OR REPLACE DATABASE  DagsterDB;

-- Below network rule and External Access INtegration is used to download any data required. This is optional

 CREATE NETWORK RULE allow_all_rule
    TYPE = 'HOST_PORT'
    MODE= 'EGRESS'
    VALUE_LIST = ('0.0.0.0:443','0.0.0.0:80');

CREATE EXTERNAL ACCESS INTEGRATION allow_all_eai
  ALLOWED_NETWORK_RULES = (allow_all_rule)
  ENABLED = true;

GRANT USAGE ON INTEGRATION allow_all_eai TO ROLE DAGSTER_ROLE;

GRANT USAGE, MONITOR ON COMPUTE POOL PR_CPU_S TO ROLE DAGSTER_ROLE;

-- GRANT OWNERSHIP ON THE DB TO THE CUSTOM ROLE
GRANT OWNERSHIP ON DATABASE DagsterDB TO ROLE DAGSTER_ROLE COPY CURRENT GRANTS;
GRANT OWNERSHIP ON ALL SCHEMAS IN DATABASE DagsterDB TO ROLE DAGSTER_ROLE COPY CURRENT GRANTS;

CREATE OR REPLACE WAREHOUSE small_warehouse WITH
  WAREHOUSE_SIZE='X-SMALL';

GRANT USAGE ON WAREHOUSE small_warehouse TO ROLE DAGSTER_ROLE;

GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE DAGSTER_ROLE;

-- Creating medium CPU compute pool
CREATE COMPUTE POOL PR_CPU_S
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_S
  AUTO_RESUME = FALSE
  INITIALLY_SUSPENDED = FALSE
  COMMENT = 'For Dagster UI' ;

-- Creating  CPU compute pool for Service Jobs (used in the assets)
CREATE COMPUTE POOL PR_STD_POOL_XS
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_XS
  AUTO_RESUME = FALSE
  INITIALLY_SUSPENDED = FALSE
  COMMENT = 'For Job Service' ;

-- Creating  CPU compute pool for Service Jobs (used in the assets)
CREATE COMPUTE POOL PR_STD_POOL_S
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_S
  AUTO_RESUME = FALSE
  INITIALLY_SUSPENDED = FALSE
  COMMENT = 'For Job Service' ;

GRANT USAGE, MONITOR, OPERATE ON COMPUTE POOL PR_CPU_S TO ROLE DAGSTER_ROLE;
GRANT USAGE, MONITOR, OPERATE ON COMPUTE POOL PR_STD_POOL_S TO ROLE DAGSTER_ROLE;
GRANT USAGE, MONITOR, OPERATE ON COMPUTE POOL PR_STD_POOL_XS TO ROLE DAGSTER_ROLE;

SHOW COMPUTE POOLS LIKE 'PR_%';

-- Change the username
GRANT ROLE DAGSTER_ROLE TO USER <username>;

USE ROLE DAGSTER_ROLE;
USE DATABASE DagsterDB;
USE WAREHOUSE small_warehouse;
USE SCHEMA PUBLIC;

CREATE IMAGE REPOSITORY IF NOT EXISTS IMAGES;

CREATE STAGE SPECS ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') ;

-- CHECK THE IMAGE RESGITRY URL

SHOW IMAGE REPOSITORIES;

-- Example output for the above query (image repository):
-- <orgname>-<acctname>.registry.snowflakecomputing.com/DagsterDB/public/images

```

### 2. Build and Push the Dagster custom Docker Image to SPCS

Edit the Makefile and update the value for SNOWFLAKE_REPO? and IMAGE_REGISTRY. This should be your image repository URL. After making the required changes, run the following command from your terminal and ensure you in the folder which has the dockerfile and the makefile. Make the changes to SNOWFLAKE_REPO , IMAGE_REGISTRY and LOGIN_NAME in the Makefile.

``` bash
make all
```

> Note: Above command will build the custom images and pushes it to the SPCS image repositories.

### 3. Upload the SPCS YAML files 

Edit the below yaml file and update the image field( should be your image repository that you have created) and upload it to `specs` internal stage.

[dagster-ui-spec.yaml](dagster-spcs/dagster-ui-spec.yaml)

Update your orgname and the accoutname in the YAML file before uploading it to the specs stage.


### 4. Creating Services for Dagster

Run the following commands to create Snowpark Container services for Dagster web server and deamon servies. Both are running in the same container.

```sql
USE ROLE DAGSTER_ROLE;
USE DATABASE DagsterDB;
USE WAREHOUSE small_warehouse;
USE SCHEMA PUBLIC;

-- Creating Dagster Service
CREATE SERVICE dagster_ui
  IN COMPUTE POOL PR_CPU_S
  FROM @specs
  SPEC='dagster-ui-spec.yaml'
  EXTERNAL_ACCESS_INTEGRATIONS = (ALLOW_ALL_EAI)
  MIN_INSTANCES=1
  MAX_INSTANCES=1;

-- Checking status of the service. Move ahead when the status is READY
SELECT SYSTEM$GET_SERVICE_STATUS('dagster_ui',1); 

-- Checking the logs of the dasgter container
SELECT value AS log_line
FROM TABLE(
 SPLIT_TO_TABLE(SYSTEM$GET_SERVICE_LOGS('dagster_ui', 0, 'dagster'), '\n')
);
```

### 5. Access Dagster UI

Once the dagster service is up and running, get the service endpoint by running the following command.
```sql
show endpoints in service dagster_ui;

SELECT "ingress_url" FROM table(RESULT_SCAN(LAST_QUERY_ID(-1)));
```
![endpoints](/dagster_ui.png)

When you access the endpoint after logging in, below is the type of the content you will see which implies ES is running fine.

```json
{
  "name" : "statefulset-0",
  "cluster_name" : "es_cluster",
  "cluster_uuid" : "oXGP1hTAQBqV8cSP1uZc5w",
  "version" : {
    "number" : "8.14.2",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "2afe7caceec8a26ff53817e5ed88235e90592a1b",
    "build_date" : "2024-07-01T22:06:58.515911606Z",
    "build_snapshot" : false,
    "lucene_version" : "9.10.0",
    "minimum_wire_compatibility_version" : "7.17.0",
    "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "You Know, for Search"
}
```

### 6. Launching Kibana

Run the following query in snowsight to get the endpoint URL of kibana.  Below query should give you endpoints in the ingress_url column.  Get the value for http.
```sql
show endpoints in service kibana_svc;
```

When you launch the endpoint after logging in you will be asked to `Configure Elastic` or enter the enrollment token. This is asked as we are not using any credentials for the Elastic Search. 

Here you can clik on `Configure manually` and enter `http://elasticsearcg-svc:9200`. After you provide the elastic search url it will prompt to enter the `Verification-code ` which you can find from the Kibana container logs.

```sql
SELECT value AS log_line
FROM TABLE(
 SPLIT_TO_TABLE(SYSTEM$GET_SERVICE_LOGS('kibana_svc', 0, 'kibana-container'), '\n')
  );
  ```

In the logs you will see a line at the end for the `verification code` and use that code and click on verify which will launch home page:

`Your verification code is:  124 602 `


By now you are all set to use Kibana and you can use sample data to load data into Elastic Search use dev tool to view the data from the same console.

![kibana](/kibana.png)

### 7. Cleanup

```sql

drop service kibana_svc;

drop service elasticsearcg_svc FORCE; 

drop compute pool PR_CPU_M;
