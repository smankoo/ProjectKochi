import os
import logging
import boto3
import datetime
from botocore.exceptions import ClientError
# from config import config

local_file_path = "/tmp/test.txt"
bucket_name = "projectkochi-downloads"
bucket_path = "downloads"

def get_s3_path(download_id):
    object_name = "/".join([bucket_path, download_id])
    return object_name

def save_file_to_bucket(download_id, local_file_path):
    """Upload downloaded file to an S3 bucket

    :param download_id: id under which the download should be uploaded
    :param local_file_path: local path of the file to be uploaded
    :return: True if file was uploaded, else False
    """

    file_name = os.path.basename(local_file_path)

    # d = str(datetime.date.today())

    object_name = get_s3_path(download_id) + '/' + file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(
            local_file_path, bucket_name, object_name, ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_download_url(download_id):

    s3_path = get_s3_path(download_id)

    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_path)
    if len(response['Contents']) != 1:
        return False

    object_key = response['Contents'][0]['Key']
    
    # s3.download_file(bucket_name, object_name)
    # bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)
    object_url = "https://{0}.s3.amazonaws.com/{1}".format(bucket_name, object_key)

    return object_url


if __name__ == '__main__':
    print("uploading file...")
    save_file_to_bucket("xxxxxx", local_file_path)
    print("upload complete.")
    print("downloading file...")
    print(get_download_url("xxxxxx"))
    print("download complete.")
