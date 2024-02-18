import io
import logging
import os as os
import urllib.parse as pars
import random
import shutil as shutil 
import sys
from pathlib import Path

import boto3
import dotenv as dotenv
from PIL import Image
import praw as praw
import requests as requests

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


dotenv.load_dotenv()


def _create_reddit_client():
    client = praw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        user_agent=os.environ["USER_AGENT"],
    )
    return client


def _is_image(post):
    try:
        return post.post_hint == "image"
    except AttributeError:
        return False


def _get_image_urls(client: praw.Reddit, subreddit_name: str, limit: int):
    hot_memes = client.subreddit(subreddit_name).hot(limit=limit)
    image_urls = list()
    for post in hot_memes:
        if _is_image(post):
            image_urls.append(post.url)

    return image_urls


def _get_image_name(image_url: str) -> str:
    image_name = pars.urlparse(image_url)

    return os.path.basename(image_name.path)


def _create_folder(folder_name: str):
    """
    If the folder does not exist then create the
    folder using the given name
    """
    if not Path(folder_name).is_dir():
        try: 
            os.mkdir(folder_name)
        except OSError as Exception:
            LOGGER.error(f"Error occured while creating {folder_name}: {Exception}")
        else:
            LOGGER.info(f"{folder_name} created")

def _compress_and_download_image(folder_name: str, raw_response, image_name: str, quality = 30):
    _create_folder(f"backend/data/{folder_name}")
    image = Image.open(io.BytesIO(raw_response.data))
    
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='JPEG', quality = quality)
    output_buffer.seek(0)
    compressed_size = sys.getsizeof(output_buffer)

    with open(f"backend/data/{folder_name}/{image_name}", "wb") as image_file:
        image_file.write(output_buffer.read())
        LOGGER.info(f"Downloaded image at {folder_name}/{image_name} and compressed from {sys.getsizeof(raw_response.data)} to {compressed_size}")

def create_s3_bucket(s3, bucket_name, folder_name):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    if 'Contents' in response:
        LOGGER.info(f"Folder '{folder_name}' already exists in bucket '{bucket_name}'.")
    else:
        s3.put_object(Bucket=bucket_name, Key=folder_name + '/')
        LOGGER.info(f"Folder '{folder_name}' created successfully in bucket '{bucket_name}'.")

def _upload_to_s3(folder_name, image_name, s3_bucket_name):
    s3 = boto3.client('s3')

    create_s3_bucket(s3,s3_bucket_name,folder_name)
    
    with open (f"backend/data/{folder_name}/{image_name}", "rb") as _file:
        s3.upload_fileobj(_file, s3_bucket_name, f"{folder_name}/{image_name}")
        LOGGER.info(f"uploaded {folder_name}/{image_name} to {s3_bucket_name}/{folder_name}/{image_name}")


def _collect_memes(subreddit_name: str, limit: int = 20, upload_to_s3:bool = False):
    """
    Collects the images from the urls and stores them into
    the folders named after their subreddits
    """
    client = _create_reddit_client()
    images_urls = _get_image_urls(
        client=client, subreddit_name=subreddit_name, limit=limit
    )
    for image_url in images_urls:
        image_name = _get_image_name(image_url)
        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            response.raw.decode_content = True
            _compress_and_download_image(subreddit_name,response.raw,image_name)
            if upload_to_s3:
                _upload_to_s3(subreddit_name, image_name, "jay-meme-generator")

if __name__ == "__main__":
    for _ in range(20):
        subreddits = os.environ['SUBREDDITS'].split(",")
        _collect_memes(random.choice(subreddits), limit=5, upload_to_s3=True)
