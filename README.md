# Dataflow Template: ES2BQ

## Description

This repository contains the ES2BQ Apache Beam Dataflow template designed to streamline data transfers from Elasticsearch to BigQuery. 

## Prerequisites

* Python 3.x  - tested for Python 3.9
* ElasticSearch - tested for ElasticSearch 7.17.x
* Google Cloud BigQuery Python client library (`google-cloud-bigquery`)
* apache-beam[gcp]



**Key Features:**

* Dynamic segmentation
* Dynamic filtering
* Configurable write dispositions
* Schema auto-detection

## Parameters

| Parameter            | Description                                               | Example                                    |
|----------------------|-----------------------------------------------------------|--------------------------------------------|
| es_endpoint          | The URL endpoint of your Elasticsearch instance           ||
| es_index             | The name of the Elasticsearch index to query              ||
| es_query             | Elasticsearch query filters (see Elasticsearch documentation) |'[{ "match_all": {} }]'|
| username             | Elastic Username ||
| password             | Elastic password ||
| bq_schema_string     | JSON string defining the BigQuery table schema            | '[{ "name": "field_1", "type": "STRING" }]' | 
| bq_project           | Google Cloud project ID containing the BigQuery dataset   | 'your-gcp-project-id'                      |
| bq_dataset           | Name of the BigQuery dataset                              | 'your_dataset_name'                        |
| bq_table             | Name of the target BigQuery table                         | 'your_target_table'                        |
| bq_write_disposition | WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY             | 'WRITE_APPEND'                             |
| field_to_segment_by | Field name to paralilise elastic records             |                             |


## Usage Instructions

### Creating the Template
 1 create/update template
```bash

  python es2bq.py \
   --runner DataflowRunner \
   --project <GCP_Project> \
   --staging_location gs://<GCS folder>/ \
   --template_location gs://<GCS template folder>/<template name> \
    --sdk_container_image <GCP region>-docker.pkg.dev/<GCP_Project>/<template name>/<docker name>:<tag> \
    --sdk_location=container
```

   2 Copy es2bq_metadata to  gs://<GCS template folder>

### Running the Template

  A) CREATE JOB FROM TEMPLATE
   1 Go to "CREATE JOB FROM TEMPLATE"

   2 Dataflow template - choose "Custom Tamplate"

   3 Template path: gs://`<GCS template folder>`
   
 B) Run locally from template: (you need to have )
  ```bash
    python -m es2bq \
      --region <GCP region> \
      --runner DataflowRunner \
      --project <GCP_Project> \
      --sdk_container_image europe-west2-docker.pkg.dev/<GCP_Project>/<template name>/<docker name>:<tag> \
      --sdk_location=container \
      --temp_location  gs://<GCS folder>/ \
      --staging_location  gs://<GCS folder>/ \
      --worker_machine_type=n2-standard-8 \ 
      --es_endpoint=<es_endpoint> \
      --es_index=<es_index> \
      --es_query='{"range": {"timestamp": {"gte":"2023-03-03","format":"yyyy-MM-dd"} }  }' \ 
      --bq_schema_string='[{  "name": "field_1",  "type": "STRING"},{  "name": "field_2",  "type": "STRING"}, ...]' \
      --username=<elastic username> \
      --password=<elastic password> \
      --bq_project=<GCP_Project> \
      --bq_dataset=<GCP dataset> \
      --bq_table=<GCP table> \
      --bq_write_disposition=WRITE_TRUNCATE \
      --field_to_segment_by=_Not_given_
  ```

C) Run template from request

  
