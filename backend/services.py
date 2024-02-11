from typing import List
import os as _os
import random as _random


def _get_image_filenames(directory_name: str) -> List[str]:
    return _os.listdir(directory_name)


def select_random_image(directory_name: str) -> str:
    images = _get_image_filenames(f"data/{directory_name}")
    random_image = _random.choice(images)
    path = f"data/{directory_name}/{random_image}"
    return path

def select_image() -> str:
    subreddit_list = ["memes","wholesomememes","2meirl4meirl","dankmemes","eyebleach","funny","happy","meirl","OneOrangeBrainCell"]
    random_subreddit = _random.choice(subreddit_list)
    return select_random_image(random_subreddit)