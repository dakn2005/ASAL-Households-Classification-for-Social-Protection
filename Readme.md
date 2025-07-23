# Household Classification for Social Protection

### Table of contents

<!-- - [Household Classification for Social Protection](#household-classification-for-social-protection) -->
- [Household Classification for Social Protection](#household-classification-for-social-protection)
    - [Table of contents](#table-of-contents)
    - [Introduction](#introduction)
    - [Problem Statement](#problem-statement)
  - [Objective](#objective)
    - [Data Sources](#data-sources)
      - [Data (Schema)](#data-schema)
    - [Technologies](#technologies)
  - [Reproducability](#reproducability)
  - [Data Pipeline](#data-pipeline)
    - [Data Ingestion](#data-ingestion)
  - [Conclusion](#conclusion)

---
---

### Introduction
We'll be looking to develop a classification model to aide in providing humanitarian aide in Arid and Semi-Arid (ASAL) regions all-over the world, through targeting affected households and providing relief (either cash on in-Kind). The model will be built upon pre-existing works [PROSPERA - Mexico](https://www.developmentpathways.co.uk/blog/the-demise-of-mexicos-prospera-programme-a-tragedy-foretold/), [HSNP - Kenya](https://ndma.go.ke/hunger-safety-net-programme-hsnp/), using data-sets already develeped using Proxy Means Testing

We'll be using data from HSNP (Kenya), building a classification model and operationalizing it using learnings from [MLOPs Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp/tree/main)

### Problem Statement
Create a production-ready classification model for easy household targeting using MLOPs methodologies

## Objective
Use Machine Learning Operations (MLOPs) methodologies to operationalize household classification model. Some interesting insights will be:
1. Feature engineering and analysis
2. Accuracy metrics from model building using MlFlow (during training)
3. model metrics from evidently

### Data Sources


#### Data (Schema)
The data contains the fields below:


### Technologies
- Docker (containerization)
- Terraform (infrastructure as code) - decided on using Terraform for tools uniformity
- Mage
- Google Cloud Storage (data lake)
- MLFlow
- Evidently
- Pocketbase

## Reproducability
<details>
<summary>GCP Setup</summary>

- Follow the GCP instructions in setting up a project

- We set up a service account to aide Kestra/Terraform/Other infrastructure tool in accessing the GCP platform.

- Configure the GCP service account by accessing I&M and Admin -> service accounts -> create service account. Add the required roles (Bigquery Admin, Compute Admin and Storage Admin)

- To get the service account key, click on the dropdown -> manage keys -> create key (choose JSON). This downloads the key to be used in Kestra to setup Bigquery db and Bucket in this instance

</details>

<details>
<summary>Kestra Setup</summary>
Ensure to docker is setup and installed as per your operating system (ensure docker engine is installed). Follow the instructions [here](https://docs.docker.com/engine/install/).

Go the [kestra website](https://kestra.io/docs/getting-started/quickstart#start-kestra) -> get Started -> goto the commands code.

```
docker run --pull=always --rm -it -p 8080:8080 --user=root -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp kestra/kestra:latest server local
```

Ensure to run the hello-world command to ensure docker is properly running

```
 sudo docker run hello-world
```

</details>

<details>
<summary>Infrastracture setup with Kestra</summary>

> Instead of using Terraform for this assignment, I preferred using a singular tool for the Infrastracture setup

Setup kestra with the format below. This will be saved as a flow

```
id: 04_gcp_kv
namespace: zoomcamp

tasks:
  - id: gcp_project_id
    type: io.kestra.plugin.core.kv.Set
    key: GCP_PROJECT_ID
    kvType: STRING
    value: [your project id] # unique project id

  - id: gcp_location
    type: io.kestra.plugin.core.kv.Set
    key: GCP_LOCATION
    kvType: STRING
    value: [location value e.g. US or us-central1]  #your preferred location

  - id: gcp_bucket_name
    type: io.kestra.plugin.core.kv.Set
    key: GCP_BUCKET_NAME
    kvType: STRING
    value: [bucket name] # make sure it's globally unique!

  - id: gcp_dataset
    type: io.kestra.plugin.core.kv.Set
    key: GCP_DATASET
    kvType: STRING
    value: [dataset name e.g. zoomcamp]
```

> ensure to set GCP_CREDS - the downloaded json key file from GCP setup
> Go to Kestra -> Namespaces -> your namespace -> KV Store -> New Key-Value -> set the GCP_CREDS key (select JSON) -> copy-paste the json key

Create another flow for setup

```
id: 05_gcp_setup
namespace: zoomcamp

tasks:
  - id: create_gcs_bucket
    type: io.kestra.plugin.gcp.gcs.CreateBucket
    storageClass: REGIONAL
    name: "{{kv('GCP_BUCKET_NAME')}}"
    ifExists: SKIP

  - id: create_bq_dataset
    type: io.kestra.plugin.gcp.bigquery.CreateDataset
    name: "{{kv('GCP_DATASET')}}"
    ifExists: SKIP

pluginDefaults:
  - type: io.kestra.plugin.gcp
    values:
      serviceAccount: "{{kv('GCP_CREDS')}}"
      projectId: "{{kv('GCP_PROJECT_ID')}}"
      location: "{{kv('GCP_LOCATION')}}"
      # bucket: "{{kv('GCP_BUCKET_NAME')}}"
```

</details>

<details>
<summary>Bigquery LLM setup</summary>
Follow the steps below to integrate LLM Model in Bigquery

1. create an external connection: Go to Add Data -> search for vertex AI -> input connection ID; be cognizant of the Region as per your setup
![LLM Setup](public/llm_setup.png)

2.  Once setup, go to the connection, copy the service ID
3.  Add a principle, with the Vertex AI user role, add the service ID as the New Principal's name
4.  Add a model, described in [this document](Dev_Readme.md)
5.  Follow the sample code from [this document](Dev_Readme.md)
</details>

## Data Pipeline
The pipelines ran 2 **Batch** jobs periodically. The pipeline architecture is as below:

![landing page](public/IaC.png)

The steps employed are:
  -  Extract (get data from source, in this case the [planecrashinfo](https://www.planecrashinfo.com/) website)
  - Load - convert data from the website into CSVs -> this is then saved in a bucket on Google Cloud Storage -> which is then loaded into an external table
  - Transform - convert into analytics views from the external table. The processes are described below in the [dbt cloud section](#transformation-using-dbt-cloud)

### Data Ingestion
I use Kestra for Orchestration of the batch jobs; Orchestration is the process of bringing together disparate activities into a continuous workflow, normally given the monicker 'flow'.

- Plane Incidents flow - Gets data from the web into a CSV file on gcs bucket

![plane incidents flow](public/flow_extract.png)

- Sentiments flow - populates the ml_classification column using summary text classified by gemini LLM

![sentiments flow](public/flow_sentiment%20analysis.png)



## Conclusion