import argparse
import logging.config
import sys

# AWS SDK
import boto3
import uuid

# Azure SDK
import adal

# GCP SDK
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient import discovery as gce_discovery, errors as gce_errors

# Azure Credentials
AZURE_ARM_SUBSCRIPTION_ID = '34756967-9f64-4a4a-93b3-b06a39270919'
AZURE_CLIENT_ID = '7f592508-ef15-4588-9e41-4721f2de5dce'
AZURE_TENANT_ID = '0fef6ba1-a8bb-4be5-b391-442297a1a751'
AZURE_SECRET_KEY = 'Cfdan5vimpckC/MaVREkPYv4NYBfMOq4Ef8Wy6UF7iQ='
RESOURCE = 'https://api.partnercenter.microsoft.com'
GRANT_TYPE = 'client_credentials'

# GCP Scopes
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/cloud-platform']


def main(args=None):

    logging.info('ARGS {}'.format(args))

    if not args:
        logging.error('At least one argument is required.')
        return 0

    if args.cloud == 'gcp':

        logging.info('Executing GCP Sample.')
        logging.info("Getting GCP Credentials from a File.")

        scopes = SCOPES
        credentials = service_account.Credentials.from_service_account_file(
            filename='/Users/pabloperez/Repositories/python-api-clouds/src/credentials/gcp/test20200111-53a51087f302.json',
            scopes=scopes,
            subject="test@ctl.io"
            )

        service = gce_discovery.build('cloudresourcemanager', 'v1', credentials=credentials, cache_discovery=False)

        logging.info('Credentials validated. Service Returned.'.format(service))
    
    elif args.cloud == 'aws':

        logging.info('Executing AWS Sample.')
        
        # 1. Environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
        # 2. Credentials file (~/.aws/credentials)

        s3client = boto3.client('s3')

        logging.info('Credentials validated. S3Client Returned.'.format(s3client))

        # Everything uploaded to Amazon S3 must belong to a bucket. These buckets are
        # in the global namespace, and must have a unique name.
        #
        # For more information about bucket name restrictions, see:
        # http://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
        bucket_name = 'python-sdk-sample-{}'.format(uuid.uuid4())
        logging.info('Creating new bucket with name: {}'.format(bucket_name))
        s3client.create_bucket(Bucket=bucket_name)

        # Now the bucket is created, and you'll find it in your list of buckets.

        list_buckets_resp = s3client.list_buckets()
        logging.info('List of buckets {}'.format(len(list_buckets_resp)))

        for bucket in list_buckets_resp['Buckets']:
            if bucket['Name'] == bucket_name:
                logging.info('(Just created) --> {} - there since {}'.format(
                    bucket['Name'], bucket['CreationDate']))

        # Files in Amazon S3 are called "objects" and are stored in buckets. A
        # specific object is referred to by its key (i.e., name) and holds data. Here,
        # we create (put) a new object with the key "python_sample_key.txt" and
        # content "Hello World!".

        object_key = 'python_sample_key.txt'

        logging.info('Uploading some data to {} with key: {}'.format(
            bucket_name, object_key))
        s3client.put_object(Bucket=bucket_name, Key=object_key, Body=b'Hello World!')

        # Using the client, you can generate a pre-signed URL that you can give
        # others to securely share the object without making it publicly accessible.
        # By default, the generated URL will expire and no longer function after one
        # hour. You can change the expiration to be from 1 second to 604800 seconds
        # (1 week).

        url = s3client.generate_presigned_url(
            'get_object', {'Bucket': bucket_name, 'Key': object_key})
        logging.info('\nTry this URL in your browser to download the object:')
        logging.info('URL : {}'.format(url))

        try:
            selected = input('Prompt :')
        except NameError:
            pass
        
        input('\nPress enter to continue...')

        # As we've seen in the create_bucket, list_buckets, and put_object methods,
        # Client API requires you to explicitly specify all the input parameters for
        # each operation. Most methods in the client class map to a single underlying
        # API call to the AWS service - Amazon S3 in our case.
        #
        # Now that you got the hang of the Client API, let's take a look at Resouce
        # API, which provides resource objects that further abstract out the over-the-
        # network API calls.
        # Here, we'll instantiate and use 'bucket' or 'object' objects.

        logging.info('\nNow using Resource API')
        # First, create the service resource object
        s3resource = boto3.resource('s3')
        # Now, the bucket object
        bucket = s3resource.Bucket(bucket_name)
        # Then, the object object
        obj = bucket.Object(object_key)
        logging.info('Bucket name: {}'.format(bucket.name))
        logging.info('Object key: {}'.format(obj.key))
        logging.info('Object content length: {}'.format(obj.content_length))
        logging.info('Object body: {}'.format(obj.get()['Body'].read()))
        logging.info('Object last modified: {}'.format(obj.last_modified))

        # Buckets cannot be deleted unless they're empty. Let's keep using the
        # Resource API to delete everything. Here, we'll utilize the collection
        # 'objects' and its batch action 'delete'. Batch actions return a list
        # of responses, because boto3 may have to take multiple actions iteratively to
        # complete the action.

        logging.info('\nDeleting all objects in bucket {}.'.format(bucket_name))
        delete_responses = bucket.objects.delete()
        for delete_response in delete_responses:
            for deleted in delete_response['Deleted']:
                logging.info('\t Deleted: {}'.format(deleted['Key']))

        # Now that the bucket is empty, let's delete the bucket.

        logging.info('\nDeleting the bucket.')
        bucket.delete()

    elif args.cloud == 'azure':
        logging.info('Executing Azure Sample.')

        authority_url = 'https://login.microsoftonline.com/'+ AZURE_TENANT_ID
        context = adal.AuthenticationContext(authority_url)
        token = context.acquire_token_with_client_credentials(
            resource=RESOURCE,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_SECRET_KEY
        )

        logging.info('Credentials validated. Token Returned. [{}]'.format(token["accessToken"]))

    else:
        logging.info('No argument matches. Please, select aws, azure or gcp.')
        pass

    return 0
