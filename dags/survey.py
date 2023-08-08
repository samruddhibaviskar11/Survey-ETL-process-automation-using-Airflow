from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta
from airflow.operators.dummy import DummyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models import Variable
from pymongo import MongoClient
from random import randint
from datetime import date
import pandas as pd
import os

mydir=os.path.join(os.getcwd(),"dags/")

#f = open("dags/count.txt", "r")
#count = f.read()
#count=int(count)
count=0
df = pd.read_csv(mydir+"answers.csv",encoding = "ISO-8859-1")

# ================================custom functions=============================

def myfunction():
    with open(mydir+'date.txt') as f:
        lines = f.readlines()
    for i in lines:
        if str(date.today()) not in i:
            global count
            _id = []
            body = []
            question = []
            ct=[]
            ut=[]
            ct1=[]
            ut1=[]
            date1 = list(pd.date_range("2021-04-02",periods=200))
            #date2 = list(pd.date_range("2021-12-22",periods=200))
            for i in range(0,len(df["updatedAt"])):
                temp =df["updatedAt"][i].split("T")[0]
                
                
                if(temp==str(date1[count]).split(" ")[0]):
                    
                    _id.append(df['_id'][i])
                    body.append(df['Body.'][i])
                    question.append(df["question"][i])
                    ct.append(df["createdAt"][i].split("T")[1])
                    ut.append(df["updatedAt"][i].split("T")[1])
                    #ct1.append(str(date2[count]).split(" ")[0])
                    #ut1.append(str(date2[count]).split(" ")[0])
            
            
            #client = MongoClient(port=27017)
            client = MongoClient( host= '192.168.0.104', port=27017,
                          username='root',
                         password='rootpassword')
            db=client.answers
            for x in range(len(_id)):
                business = {
                    '_id' : _id[x],
                    'Body.' : body[x],
                    #'createdAt' : ct1[x]+"T"+ct[x],
                    'createdAt' : str(date.today())+"T"+ct[x],
                    'question' : question[x],
                    #'updatedAt' : ut1[x]+"T"+ut[x]
                    'updatedAt' : str(date.today())+"T"+ut[x]
                    }
                result=db.data.insert_one(business)
            count+=1
            with open(mydir+'count.txt','w') as file1:
                file1.write(str(count))
            with open(mydir+'date.txt','w') as file2:
                    file2.write(str(date.today()))

# ===============================================================================



# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(seconds=120)
}

dag=DAG('survey',
         start_date=datetime(2021, 12, 22),
         max_active_runs=2,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) 

start_ = DummyOperator(
        task_id='start',
        dag=dag,
        )

# Step 4 - Create a Branching task to Register the method in step 3 to the branching API


myfunction = PythonOperator(
  task_id='myfunction',
  python_callable=myfunction, #Registered method
  provide_context=True,
  dag=dag
)




end_dummy = DummyOperator(
    task_id='end',
    dag=dag,
    )

start_ >> myfunction>>end_dummy
