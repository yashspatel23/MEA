# -*- coding: utf-8 -*-
import time

import botocore

import cPickle as pickle


def s3_create_bucket(s3, bucket):
    buckets = []
    for _bucket in s3.buckets.all():
        buckets.append(_bucket.name)
    if bucket not in buckets:
        s3.create_bucket(Bucket=bucket)
        time.sleep(1)  # wait for bucket creation


def s3_delete_folder(s3, bucket, folder):
    """
    folder name in string
    """
    bucket_con = s3.Bucket(bucket)
    for obj in bucket_con.objects.filter(Prefix=folder, MaxKeys=9999):
        s3.Object(bucket, obj.key).delete()


def s3_delete_key(s3, bucket, key):
    """
    Deleting a key. Does not work for a folder.
    """
    return s3.Object(bucket, key).delete()


def s3_key_exist(s3, bucket, key):
    """
    A key refers to an concrete object. A folder is not an object.
    """
    try:
        s3.Object(bucket, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = False
        else:
            raise e
    else:
        exists = True
    
    return exists


def s3_put_str(s3, bucket, key, value):
    return s3.Object(bucket, key).put(Body=value)


def s3_put_obj(s3, bucket, key, obj):
    pickled = pickle.dumps(obj)
    return s3.Object(bucket, key).put(Body=pickled)


def s3_put_file(s3, bucket, key, file_path):
    s3_create_bucket(s3, bucket)
    with open(file_path, 'r') as f:
        s = f.read()
    return s3.Object(bucket, key).put(Body=s)


def s3_get_str(s3, bucket, key):
    try:
        s3_object = s3.Object(bucket, key).get()
        s = s3_object['Body'].read()
    except botocore.exceptions.ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            s = None
        else:
            raise e
    return s


def s3_get_obj(s3, bucket, key):
    try:
        s3_object = s3.Object(bucket, key).get()
        pickled = s3_object['Body'].read()
        obj = pickle.loads(pickled)
    except botocore.exceptions.ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            obj = None
        else:
            raise e
    return obj


if __name__ == '__main__':
#     bucket = AWS_S3_CACHE_BUCKET
#     
#     
#     AWS_S3_CACHE_BUCKET
#     'healthgraph-scrapy-cache'
#     
#     print s3_put_str(s3, 'healthgraph-scrapy-cache', 'aaa/111.txt', 'jh jh jh')
#     print s3_key_exist(s3, 'healthgraph-scrapy-cache', 'aaa/111.txt')
#     print s3_delete_folder(s3, 'healthgraph-scrapy-cache', 'aaa')

#
#
#     s3.Object('healthgraph-scrapy-cache', 'aaa/222.txt').delete()
#     
#     bucket = s3.Bucket('healthgraph-scrapy-cache')
#     for obj in bucket.objects.filter(Prefix='spider__mayo/'): print obj.key
#
#     for obj in bucket.objects.filter(Prefix='aaa'): print obj.key
#
#         s3.Object(bucket.name, obj.key).delete()
    pass
