import os
import re

from datetime import datetime
from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults
from airflow.sensors.base import BaseSensorOperator


class ArchiveFileOperator(BaseOperator):
    @apply_defaults
    def __init__(self, filepath, archivepath, *args, **kwargs):
        super(ArchiveFileOperator, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.archivepath = archivepath

    def execute(self, context):
        file_name = context['task_instance'].xcom_pull(
            'file_sensor_task', key='file_name')
        os.rename(self.filepath + file_name, self.archivepath + file_name)


class OmegaFileSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, filepath, filepattern, *args, **kwargs):
        super(OmegaFileSensor, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.filepattern = filepattern

    def poke(self, context):
        full_path = self.filepath
        filepattern = self.filepattern
        extention = filepattern.split(".")[1].replace(")","")
        #print(extention)
        filepattern = full_path.replace("/","\/")+filepattern
        file_pattern = re.compile(filepattern)
        try:
        #######################################
          for dirpath, subdirs, files in os.walk(full_path):
              for x in files:
                  if x.endswith(f"{extention}"):
                      print("found",os.path.join(dirpath, x))
              
                      #if re.match(file_pattern, os.path.join(dirpath, x)):
                      context['task_instance'].xcom_push('file_name', str(os.path.join(dirpath, x)))
                      return True
          print("searching for new files!")
          return False
        except:
            print("Trying hard to find a file that match with this pattern",filepattern)
            return False
        """try:
          #######################################
            for x in os.walk(full_path):
                files = x[0]+"/"+x[2][0]
                if re.match(file_pattern, files):
                    context['task_instance'].xcom_push('file_name', files)
                    return True
            print("searching for new files!")
            return False
        except:
            print("Trying hard to find a file that match with this pattern",filepattern)
            return False
        """
        #print("[",re.match(file_pattern, files)!=None,"]",files,)
        """
        directory = os.listdir(full_path)

        for files in directory:
            if re.match(file_pattern, files):
                context['task_instance'].xcom_push('file_name', files)
                return True
        print("searching for new files")
        return False
        """
 

class OmegaPlugin(AirflowPlugin):
    name = "omega_plugin"
    operators  = [OmegaFileSensor, ArchiveFileOperator] 