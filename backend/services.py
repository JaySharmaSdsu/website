from typing import List
import os as os
import random as random

import boto3

def _get_image_filenames(directory_name: str, s3: boto3) -> List[str]:
    return random.choice([images['key'] for images in s3.list_objects_v2(Bucket=os.environ['S3-BUCKET'], prefix = directory_name)['Contents']])


def select_random_image(directory_name: str, s3: boto3) -> str:
    images = _get_image_filename(directory_name, s3)
    path = f"data/{directory_name}/{random_image}"
    return path

def _get_buckets(s3:boto3) -> list[str]:
    return  [folders['Key'] for folders in s3.list_objects_v2(Bucket = os.environ['S3-BUCKET'])['Contents']]

def select_image() -> str:
    s3 = boto3.client('s3')
    random_subreddit = random.choice(_get_buckets(s3))
    return select_random_image(random_subreddit, s3)