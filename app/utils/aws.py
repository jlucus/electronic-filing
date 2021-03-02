import boto3
import logging
from app.utils.async_utils import (
    async_wrap
)
from app.core.config import (
    S3_AWS_ACCESS_KEY_ID,
    S3_AWS_SECRET_ACCESS_KEY,
    S3_AWS_REGION,
    EFILE_ENV,
)

logger = logging.getLogger("fastapi")

class AwsS3(object):
    def __init__(
        self,
        key_id=S3_AWS_ACCESS_KEY_ID,
        secret=S3_AWS_SECRET_ACCESS_KEY,
        region=S3_AWS_REGION,
    ):
        self.__key_id = key_id
        self.__secret = secret
        self.__region = region
        self.__client = boto3.client(
            "s3",
            aws_access_key_id=self.__key_id,
            aws_secret_access_key=self.__secret,
            region_name=self.__region,
        )

    @property
    def region(self):
        return self.__region

    @property
    def client(self):
        return self.__client

    def update_object_acl(self, bucket, key, ACL):

        res = self.__client.put_object_acl(ACL=ACL,
                                           Bucket=bucket,
                                           Key=key)
        return res
    
    def replace_metadata(self, bucket, key, new_metadata, ACL=''):
        new_metadata = {k: str(new_metadata[k]) for k in new_metadata}
        res = self.__client.copy_object(Key=key, Bucket=bucket,
               CopySource={"Bucket": bucket, "Key": key},
                                        Metadata=new_metadata, 
                                        MetadataDirective="REPLACE",
                                        ACL=ACL)
        return res
    
    def put_filedata(self, bucket, key, filedata, filename=None,
                     other_metadata={}, ACL=''):
        response = self.__client.list_buckets()
        buckets = [x.get("Name") for x in response.get('Buckets',[])]
        if bucket not in buckets:
            self.__create_bucket(bucket)

        metadata = {}
        if filename and isinstance(filename, str):
            metadata.update({"filename": filename})
        if other_metadata and isinstance(other_metadata, dict):
            metadata.update(other_metadata)

        # cast all metadata values to string for s3 head-object
        metadata = {k: str(metadata[k]) for k in metadata}

        put_response = self.__client.put_object(
            Bucket=bucket,
            Key=key,
            Body=filedata,
            Metadata=metadata,
            ACL=ACL
        )

        head_response = self.__client.head_object(Bucket=bucket, Key=key)

        return {"put_object": put_response, "head_object": head_response}

    async def async_put_file_data(
        self, bucket, key, filedata, filename=None, other_metadata={}
    ):
        return async_wrap(self.put_file_data)(
            self, bucket, key, filedata, filename=None, other_metadata={})
    
    def get_filedata(self, bucket, key):
        return self.__client.get_object(Bucket=bucket, Key=key)

    async def async_get_file_data(self, key, bucket):
        return async_wrap(self.get_filedata)(self, key, bucket)
    
    def get_file(self, bucket, key, outpath):
        data = self.__client.get_object(Bucket=bucket, Key=key)
        with open(outpath, 'wb') as outfile:
            for bytes in data['Body']:
                outfile.write(bytes)
            
    
    
    def __create_bucket(self, bucket):
        location = {'LocationConstraint': self.__region}
        self.__client.create_bucket(Bucket=bucket,
                                    CreateBucketConfiguration=location)

