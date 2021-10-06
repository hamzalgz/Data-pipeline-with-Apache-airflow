# from airflow.contrib.hooks.fs_hook import FSHook
#
# from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.dummy_operator    import DummyOperator
from airflow.operators.python_operator    import PythonOperator
from airflow.operators.trigger_dagrun import  TriggerDagRunOperator

#file place in /data/ds_env/..../packages-site/
from omega_plugin_file import OmegaFileSensor, ArchiveFileOperator

#installed using pip (check pip freez)
from airflow.providers.papermill.operators.papermill import PapermillOperator

import datetime
from datetime import date, timedelta
import airflow



default_args = {
    "depends_on_past" : False,
    "start_date"      : airflow.utils.dates.days_ago( 1 ),
    "retries"         : 1,
    "retry_delay"     : datetime.timedelta( hours= 5 ),
}



task_name = 'check_file'

def print_filename(**context):
  file_to_process = context['task_instance'].xcom_pull(key='file_name', task_ids="check_new_file")
  print("->>>> we will save this file : ",file_to_process)
  file = open("/home/imade/notebook/input_config.txt","w")
  file.write(file_to_process)
  file.close()
  



with airflow.DAG( "first_etl", default_args= default_args, schedule_interval= "@once"  ) as dag:
    start_task  = DummyOperator(  task_id= "start" )
    stop_task   = DummyOperator(  task_id= "stop"  )
    
    
    
    #using the defined OmegaFileSensor operator to check for new files
    sensor_task = OmegaFileSensor(
      task_id='check_new_file', #name of the task
      filepath="/home/imade/notebook/input/", #root path for checking
      filepattern=r"\b(\w*.xlsx)", #pattern used when checking domaine/date/file_json
      poke_interval=10, #time interval between file verification
      dag=dag #append task to dag
    )
    
    preparing_detected_file = PythonOperator(
      task_id="preparing_detected_file",
      python_callable=print_filename,
      #provide_context=True,
      retries=10,
      retry_delay=datetime.timedelta(seconds=1)
    )
    
    
   
    process_file_notebook = PapermillOperator(
        task_id="process_file_notebook",
        input_nb="/home/imade/notebook/process_input_list.ipynb",
        output_nb="/home/imade/notebook//outs/out-process_input_list{{ execution_date }}.ipynb",
        parameters={"msgs": "Ran from Airflow at {{ execution_date }}!"},
    )    
    
    trigger_again = TriggerDagRunOperator(
        task_id='trigger_dag_again', 
        trigger_dag_id="first_etl", 
        dag=dag
    )
   
start_task >> sensor_task >> preparing_detected_file >> process_file_notebook >> stop_task >> trigger_again