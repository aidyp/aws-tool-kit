import boto3
import os
import sys
import time

athena_qry_str = r"""
CREATE EXTERNAL TABLE `s3_access_logs_db.mybucket_logs`(
  `bucketowner` STRING,
  `bucket_name` STRING,
  `requestdatetime` STRING,
  `remoteip` STRING,
  `requester` STRING,
  `requestid` STRING,
  `operation` STRING,
  `key` STRING,
  `request_uri` STRING,
  `httpstatus` STRING,
  `errorcode` STRING,
  `bytessent` BIGINT,
  `objectsize` BIGINT,
  `totaltime` STRING,
  `turnaroundtime` STRING,
  `referrer` STRING,
  `useragent` STRING,
  `versionid` STRING,
  `hostid` STRING,
  `sigv` STRING,
  `ciphersuite` STRING,
  `authtype` STRING,
  `endpoint` STRING,
  `tlsversion` STRING)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'input.regex'='([^ ]*) ([^ ]*) \\[(.*?)\\] ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) (\"[^\"]*\"|-) (-|[0-9]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) (\"[^\"]*\"|-) ([^ ]*)(?: ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*))?.*$')
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
"""


def create_logging_bucket(source_bucket):


    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    target_bucket = source_bucket + '-access-logs'
    target_prefix = source_bucket + 'Logs/'


    # Create logging bucket
    try:
        region = os.environ['AWS_DEFAULT_REGION']
        create_bucket_response = client.create_bucket(
            Bucket=target_bucket,
            CreateBucketConfiguration={
                'LocationConstraint': 'eu-west-1'
            }
        )
    except s3.meta.client.exceptions.BucketAlreadyExists:
        # We can go ahead 
        print('Bucket already exists, enabling logging')
    except:
        #Another error, 
        pass

    # Add an ACL to the bucket 
    acl_response = client.put_bucket_acl(
        Bucket=target_bucket,
        GrantWrite='uri=http://acs.amazonaws.com/groups/s3/LogDelivery',
        GrantReadACP='uri=http://acs.amazonaws.com/groups/s3/LogDelivery'
    )
    print(acl_response)

    logs_response = client.put_bucket_logging(
        Bucket=source_bucket,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': target_bucket,
                'TargetGrants': [
                    {
                        'Grantee': {
                            'Type': 'Group',
                            'URI': 'http://acs.amazonaws.com/groups/global/AllUsers',
                        },
                        'Permission':'READ',
                    },
                ],
                'TargetPrefix': target_prefix
            },
        },
    )

    return target_bucket

def setup_athena_for_bucket(access_bucket):
    athena = boto3.client('athena')
    s3 = boto3.client('s3')
    athena_bucket = access_bucket + '-athena-query-logs'

    # Athena needs a bucket to write queries into 
    try: 
        region = os.environ['AWS_DEFAULT_REGION']
        create_bucket = s3.create_bucket(
            Bucket=athena_bucket,
            CreateBucketConfiguration={
                'LocationConstraint':region
            }
        )
    except:
        # Bucket likely already exists, but need to get exact error 
        pass 

    

    # Create a database & table schema in the database
    database_name = 's3_access_logs_db'
    config = {'OutputLocation': 's3://' + athena_bucket + '/'}
    create_database_query = athena.start_query_execution(
        QueryString = 'create database ' + database_name,
        ResultConfiguration = config
    )

    athena.update_work_group(
        WorkGroup='primary',
        ConfigurationUpdates={
            'ResultConfigurationUpdates': config
        }
    )

    context = {'Database': database_name}
    complete = False 
    while not complete:
        response = athena.get_query_execution(
            QueryExecutionId = create_database_query['QueryExecutionId']
        )
        status = response['QueryExecution']['Status']['State']
        if (status == 'FAILED') or (status == 'CANCELLED'):
            print("Database create failed")
            return 
        elif status == 'SUCCEEDED':
            complete = True 
        else:
            time.sleep(1)
    
    LOCATION = '\'' + config['OutputLocation'] + '\''
    qry = athena_qry_str + LOCATION

    athena.start_query_execution(
        QueryString=qry,
        QueryExecutionContext = context,
        ResultConfiguration = config
    )




    

if __name__ == '__main__':
    # Do something here
    try:
        source_bucket = sys.argv[1]
    except:
        print(athena_logs_setup_query_sql)
        print('Usage: python setup-access-logs.py <source_bucket>')
        sys.exit

    access_log_bucket = create_logging_bucket(source_bucket)
    print(access_log_bucket)
    setup_athena_for_bucket(access_log_bucket)