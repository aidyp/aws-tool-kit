import boto3
import os
import sys

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

    print(logs_response)

def setup_athena_for_bucket():
    

if __name__ == '__main__':
    # Do something here
    try:
        source_bucket = sys.argv[1]
    except:
        print('Usage: python setup-access-logs.py <source_bucket>')

    create_logging_bucket(source_bucket)