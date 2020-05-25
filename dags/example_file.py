import airflow
from airflow.models import DAG
from datetime import datetime, timedelta
from operators.file_compare_operator import FileCompareOperator
from protos_gen.config_pb2 import RunnerConfig, TestcaseConfig, Site

with DAG(
        dag_id='example_file',
        default_args={
            'owner': 'ouyang',
            'start_date': airflow.utils.dates.days_ago(0)
        },
        schedule_interval='@once',
) as dag:
    file_compare = FileCompareOperator(
        runner_conf=RunnerConfig(),
        task_id='file_compare',
        provide_context=True,
        jobID='manual__2020-05-12T00:55:55.479340 00:00',
        file_name='DispMD_5600000_20200512.csv'
    )

if __name__ == "__main__":
    dag.cli()