# -*- coding: utf-8 -*-
import time

import botocore

import cPickle as pickle


import gdax


if __name__ == '__main__':

    sandbox_url = 'https://api-public.sandbox.gdax.com'
    api_key = 'cc534c5f9d164e226bf408b663ec472f'
    api_secret = 'lwt1631P/8/9eFuUIftHlDxH/m+yNXLyH0+WOqiLrCxMeLOTI2Hne3Vkj0ERlOF1XZii9QOrpPvr6PEKk5mYIw=='
    passphrase = 'vb0x06vs0ce'


    auth_client = gdax.AuthenticatedClient(api_key, api_secret, passphrase, api_url=sandbox_url)

    print auth_client


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
