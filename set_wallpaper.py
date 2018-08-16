#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Set wallpapers from reddit

source:
    http://www.reddit.com/r/wallpaper/.json

1. Get image from reddit:
2. Download and move
3. Set image
4. cleanup / remove old wallpaper?

TBD:
    log source and filename to help track where awesome images came from.
"""

import os
import argparse
import logging
import requests
import numpy as np
import yaml

ROOT_PATH = '/home/aman/wallpaper-roulette'
DESTINATION_PATH = '/home/aman/Downloads/reddit_wallpaper'
LOGFILENAME = 'wallpaper_history.log'
SOURCEFILENAME = 'sources.yaml'

def reddit_post_usable(post):
    """ Return True is reddit post has usable image"""

    # Filter out urls that are not usable images
    suffixes = ['.png', '.jpg']
    has_suffix = lambda url: any([s in url for s in suffixes])

    image_url = post['data']['url']
    return has_suffix(image_url)

def get_image_url_from_reddit(source):
    """ Get image URL from a reddit source
    """
    header = {
        'User-Agent': 'n00b wallpaper bot v0.4',
        # 'Authorization': 'Client-ID ' + client_id
        }

    req = requests.get(source, headers=header)

    # Get json from URL
    json_object = req.json()

    # Get all posts from JSON object
    posts = json_object['data']['children']

    filtered_posts = [p for p in posts if reddit_post_usable(p)]
    selected_post = np.random.choice(filtered_posts)

    subreddit = selected_post['data']['subreddit']
    name = selected_post['data']['title']
    url = selected_post['data']['url']

    logging.info('[subreddit: "%s"]: %s', subreddit, name)
    logging.info('[x of %i options]: URL: %s', len(filtered_posts), url)

    return url

def download_image_from_url(url, DESTINATION_PATH):
    """
    Download image from URL
    """

    image_type = url.split('.')[-1]
    image_type = image_type.split('?')[0]

    header = {
        'User-Agent': 'n00b wallpaper bot v0.4',
        # 'Authorization': 'Client-ID ' + client_id
        }
    i = requests.get(url, stream=True, headers=header)

    outfile = "{}.{}".format(DESTINATION_PATH, str(image_type))

    with open(outfile, 'wb') as f:
        for chunk in i.iter_content(chunk_size=1024):
            f.write(chunk)
    i.raise_for_status()

    return outfile

def main(source_list):
    """Main function
    """
    source = np.random.choice(source_list)
    # print "Using source: {}".format(source)

    url = get_image_url_from_reddit(source)
    outfile = download_image_from_url(url, DESTINATION_PATH)

    # print "{} --> {}".format(url, outfile)

    setbg_command = "gsettings set org.gnome.desktop.background picture-uri"
    img_path = "file://{}".format(outfile)

    # import subprocess
    # subprocess.call([setbg_command, img_path])

    os.system("{} {}".format(setbg_command, img_path))

    return True

def get_source_list(nsfw=False):
    """Fetches source list from YAML file"""

    source_path = os.path.join(ROOT_PATH, SOURCEFILENAME)
    with open(source_path) as ff:
        sources = yaml.safe_load(ff)

    # Pick source list
    if nsfw:
        return sources['NSFW']
    else:
        return sources['Main']


if __name__ == "__main__":
    # Parse Args
    parser = argparse.ArgumentParser()

    parser.add_argument(
            "--nsfw",
            dest='use_nsfw',
            action='store_true',
            help='get image from alternate list of sources'
            )
    parser.set_defaults(use_nsfw=False)

    args = parser.parse_args()

    source_list = get_source_list(args.use_nsfw)

    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=os.path.join(ROOT_PATH, LOGFILENAME),
                        level=logging.INFO)

    logging.getLogger("requests").setLevel(logging.WARNING)

    # Start
    main(source_list)
