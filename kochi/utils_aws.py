import os
import logging
import boto3
import datetime
from botocore.exceptions import ClientError
import json
# from config import config

my_path = os.path.abspath(os.path.dirname(__file__))
config_loc = os.path.join(my_path, "../config.json")

with open(config_loc, 'r') as config_file:
    data = config_file.read()

config = json.loads(data)


def get_s3_path(download_id):
    bucket_path = config['bucket_path']
    d = str(datetime.date.today())
    object_name = "/".join([bucket_path, d, download_id])
    return object_name

def save_download_to_bucket(download_id):
    """Upload downloaded file to an S3 bucket

    :param download_id: id under which the download should be uploaded
    :param local_file_path: local path of the file to be uploaded
    :return: True if file was uploaded, else False
    """

    bucket_name = config['download_bucket']
    download_dir = config['download_dir']

    local_file_dir = os.path.join(download_dir, download_id)

    dir_contents = os.listdir(local_file_dir)
    if len(dir_contents) != 1:
        return False
    
    local_file_name = dir_contents[0]

    local_file_path = os.path.join(local_file_dir, local_file_name)

    object_name = get_s3_path(download_id) + '/' + local_file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(
            local_file_path, bucket_name, object_name, ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_s3_download_url(download_id):

    bucket_name = config['download_bucket']

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
    download_id = "0459f08d1cdd4418ae211800d8d38e8e"
    print("uploading file...")
    save_download_to_bucket(download_id)
    print("upload complete.")
    print("downloading file...")
    print(get_download_url(download_id))
    print("download complete.")
