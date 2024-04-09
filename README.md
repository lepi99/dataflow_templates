# Dataflow Template Repository

## Description
A repository for creating custom Apache Beam Dataflow templates

* **Template 1: ES2BQ** 
  * Reusable Python Dataflow template for migrating data from Elasticsearch to BigQuery. Includes features like dynamic segmentation, dynamic filtering and configurable write dispositions for seamless and adaptable pipelines.


## Usage Instructions

1. Create Template
  ` #1.1 create/update template
  python es2bq.py \
   --runner DataflowRunner \
   --project <GCP_Project> \
   --staging_location gs://<GCS folder>/ \
   --template_location gs://<GCS template folder>/<template name> \
    --sdk_container_image <GCP region>-docker.pkg.dev/<GCP_Project>/<template name>/<docker name>:<tag> \
    --sdk_location=container`

   1.2 Copy es2bq_metadata to  gs://<GCS template folder>

2. CREATE JOB FROM TEMPLATE
   2.1 Go to "CREATE JOB FROM TEMPLATE"

   2.2 Dataflow template - choose "Custom Tamplate"

   2.3 Tamplate path: gs://<GCS template folder>
   
3. Run locally from template: (you need to have )
  `python -m es2bq \
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
  `
4. Run template from request

  
