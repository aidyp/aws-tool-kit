import boto3 
import os 
import sys 
import time


def tear_down_athena(access_bucket):
    
    # Drop table, then drop database 

    athena = boto3.client('athena')
    athena_bucket = access_bucket + '-athena-query-logs'
    database_name = 's3_access_logs_db'
    table_name = 's3_access_logs_db.mybucket_logs'
    config = {'OutputLocation': 's3://' + athena_bucket + '/'}

    delete_table = athena.start_query_execution(
        QueryString = 'drop table ' + table_name,
        ResultConfiguration = config  
    )
    delete_complete = False 
    while not delete_complete:
        response = athena.get_query_execution(
            QueryExecutionId = delete_table['QueryExecutionId']
        )
        status = response['QueryExecution']['Status']['State']
        if (status == 'FAILED') or (status == 'CANCELLED'):
            print("Table drop dropped")
            return 
        elif status == 'SUCCEEDED':
            delete_complete = True 
        else: 
            time.sleep(1)
    

    delete_database = athena.start_query_execution(
        QueryString = 'drop database ' + database_name,
        ResultConfiguration = config
    )

def tear_down_s3(access_bucket):
    s3 = boto3.resource('s3')
    pass


if __name__ == '__main__':
    try:
        source_bucket = sys.argv[1] 
    except:
        print('Usage: python cleanup.py <source_bucket>')
        sys.exit(0)

    access_bucket = source_bucket + '-access-logs'
    tear_down_athena(access_bucket)