import json
import logging
import re
import typing


import apache_beam as beam
from apache_beam import FlatMap, Map, Create
from apache_beam.options.value_provider import ValueProvider
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.runners import DataflowRunner
from apache_beam.io.gcp.bigquery_tools import parse_table_schema_from_json
from elasticsearch import Elasticsearch,helpers

project= "GCP project_id"

logging.getLogger().setLevel(logging.INFO)
options = PipelineOptions(
    project=project,
    region="GCP region",
    runner="DataflowRunner"
)


class RuntimeOptions(beam.options.pipeline_options.PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--es_endpoint', type=str, help='AWS Elasticsearch endpoint', default='not_given')
        parser.add_value_provider_argument('--es_index', type=str, help='Elasticsearch index name', default='not_given')
        parser.add_value_provider_argument('--es_query', type=str, help='Optional Elasticsearch query', default='[{ "match_all": {} }]')
        parser.add_value_provider_argument('--bq_project', type=str, help='BigQuery project ID', default='not_given')
        parser.add_value_provider_argument('--bq_dataset', type=str, help='BigQuery dataset name', default='not_given')
        parser.add_value_provider_argument('--bq_table', type=str, help='BigQuery table name', default='not_given')
        parser.add_value_provider_argument('--bq_schema_string', type=str, help='BigQuery table schema in JSON string format', default='not_given')
        parser.add_value_provider_argument('--username', type=str, help='Username for Elasticsearch authentication', default='not_given')
        parser.add_value_provider_argument('--password', type=str, help='Password for Elasticsearch authentication', default='not_given')
        parser.add_value_provider_argument('--field_to_segment_by', type=str, help='Field to get unique values for', default='_Not_given_')
        parser.add_value_provider_argument('--bq_write_disposition', type=str, help='BigQuery write disposition (WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY)', default='WRITE_APPEND')


runtime_options = options.view_as(RuntimeOptions)



class FetchUniqueValuesDoFn(beam.DoFn):
    def process(self, element, es_endpoint, index, username, password,es_query, field):
        from elasticsearch import Elasticsearch
        logging.getLogger().setLevel(logging.INFO)

        logging.debug("Element: %s", element)
        print("Element" + element)
        logging.debug("es_endpoint: %s", es_endpoint.get())
        print("es_endpoint")
        print(es_endpoint.get())
        logging.debug("username: %s", username.get())
        print("username")
        print(username.get())
        logging.debug("password: %s", password.get())
        print("password")
        print(password.get())
        logging.debug("es_query: %s", es_query.get())
        print("es_query")
        print(es_query.get())
        es_client = Elasticsearch([es_endpoint.get()], http_auth=(username.get(), password.get()))
        # Aggregation query to get unique values
        if field == "_Not_given_":
            logging.info("Print the unique value string _Not_given_")
            yield ("_Not_given_")
        else:
            query = {
                "query": {
                    "bool": {
                        "filter": json.loads(es_query.get())
                    }
                },
                "aggs": {
                    "unique_values": {
                        "terms": {"field": field.get()}
                    }
                }
            }
            logging.info("Full segment query run %s", es_query.get())
            result = es_client.search(index=index.get(), body=query)
            unique_values = result['aggregations']['unique_values']['buckets']

            for item in unique_values:
                logging.info("Print the unique value string %s", unique_values)
                yield (item['key'])
            yield ("None")


class ReadFromElasticsearchDoFn(beam.DoFn):
    def process(self, key_val, es_endpoint, index, username, password,es_query, field):
        from elasticsearch import Elasticsearch, helpers
        logging.getLogger().setLevel(logging.INFO)
        es_config = {'hosts': [es_endpoint.get()]}
        es_config['http_auth'] = (username.get(), password.get())

        if field.get() == "_Not_given_":
            print("No Segments version")
            logging.info("Segment %s", field.get())
            logging.info("Get full query %s", index.get())


            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"match_all": {}}
                        ],
                        "filter": json.loads(es_query.get())
                    }
                }
            }
            logging.info("Query filter run %s", es_query.get())
            logging.info("Full query run %s", query)
        else:
            print("Version with Segments")
            logging.info("Get segments field query %s", field.get())
            logging.info("Get segments field value query %s", key_val)
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {field.get(): key_val}}
                        ],
                        "filter": json.loads(es_query.get())
                    }
                }
            }

            logging.info("Query filter run %s", es_query.get())
            logging.info("Full query run %s", query)
        #{"range": {"date_field": {"gte": "2023-12-01", "lt": "now"}}},
        #{"term": {"category": "infrastructure"}}

        es = Elasticsearch(**es_config)

        for hit in helpers.scan(es, index=index.get(), query=query):
            yield hit['_source']

class TransformDataDoFn(beam.DoFn):
    def __init__(self,runtime_options):
        self.runtime_options = runtime_options
        self.bq_schema = None

    def setup(self):
        if self.bq_schema is None:
            bq_schema = json.loads(self.runtime_options.bq_schema_string.get())
            self.bq_schema = [field['name'] for field in bq_schema]

    def process(self, record):
        bq_schema = self.bq_schema

        filtered_record = {field: str(record.get(field)) for field in bq_schema if
                       field in record and str(record.get(field)) != "None"}
        yield filtered_record


def transform_data(record, bq_schema_string):
    logging.getLogger().setLevel(logging.INFO)
    bq_schema = bq_schema_string

    filtered_record = {field: str(record.get(field)) for field in bq_schema if
                       field in record and str(record.get(field)) != "None"}


    return filtered_record

def choose_write_disposition(bq_write_disposition):
    if bq_write_disposition.get() == "WRITE_APPEND":
        return beam.io.BigQueryDisposition.WRITE_APPEND
    elif bq_write_disposition.get() == "WRITE_TRUNCATE":
        return beam.io.BigQueryDisposition.WRITE_TRUNCATE
    else:
        logging.error("Invalid write disposition %s", bq_write_disposition.get())
        raise "invalid write disposition"

def format_table_reference(bq_table, bq_project, bq_dataset):
    return lambda element: f"{bq_project.get()}:{bq_dataset.get()}.{bq_table.get()}"

pipeline = beam.Pipeline(DataflowRunner(), options)


data = (
        pipeline
        | beam.Create(["Your Query / source object qualifier goes here"])


        | 'Get Unique Values' >> beam.ParDo(FetchUniqueValuesDoFn(),
                                            runtime_options.es_endpoint,
                                            runtime_options.es_index,  # Assuming you reuse the index
                                            runtime_options.username,  # Assuming you reuse the index
                                            runtime_options.password,
                                            runtime_options.es_query,
                                            runtime_options.field_to_segment_by
                                            )
        | 'Read Segmented Data' >> beam.ParDo(ReadFromElasticsearchDoFn(runtime_options.bq_schema_string),
                                              runtime_options.es_endpoint,
                                              runtime_options.es_index,  # Assuming you reuse the index
                                              runtime_options.username,  # Assuming you reuse the index
                                              runtime_options.password,  # Assuming you reuse the index
                                              runtime_options.es_query,  # Assuming you reuse the index
                                              runtime_options.field_to_segment_by
                                              )
        | 'Transform Data' >> beam.ParDo(TransformDataDoFn(runtime_options))

        | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
    table=format_table_reference(runtime_options.bq_table, runtime_options.bq_project, runtime_options.bq_dataset),
    dataset=runtime_options.bq_dataset,
    project=runtime_options.bq_project,
    schema='SCHEMA_AUTODETECT', 
    write_disposition=choose_write_disposition(runtime_options.bq_write_disposition),
    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
)
)

pipel = pipeline.run()