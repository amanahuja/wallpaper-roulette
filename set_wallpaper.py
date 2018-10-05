#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes care of interfaces to reddit, IG and other sources
Fetches wallpapers from where specified in the file
"""

import os
import requests
import logging
import yaml
import numpy as np

# set root path to location of this file
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

class ImageFetcher: 
    """Fetches images"""
    def __init__(self) -> None:
        self.dest_path = None

    def __call__(self, source_url: str, target_dir: str) -> None:
        header = {
            'User-Agent': 'n00b wallpaper bot v0.4',
            # 'Authorization': 'Client-ID ' + client_id
            }
        i = requests.get(source_url, stream=True, headers=header)

        img_file_suffix = source_url.split('.')[-1]
        img_file_suffix = img_file_suffix.split('?')[0]

        dest_path = "{}/{}.{}".format(
            target_dir,
            'roulette_background',
            str(img_file_suffix))

        with open(dest_path, 'wb') as outfile:
            for chunk in i.iter_content(chunk_size=1024):
                outfile.write(chunk)
        i.raise_for_status()

        self.dest_path = dest_path
        # TODO: log image source and destination

        return None

class RouletteConfig:
    """Reads Roulette config file"""
    def __init__(self, config_path: str = None) -> None:
        if config_path is None:
            config_path = os.path.join(ROOT_PATH, 'sources.yaml')
        assert os.path.exists(config_path), config_path

        with open(config_path) as infile:
            config = yaml.safe_load(infile)

        self.sources = config['SOURCES']
        self.nsfw_sources = config['NSFW_SOURCES']

    def source_list(self, nsfw: bool = False):
        """get list of sources"""
        if nsfw:
            return self.nsfw_sources
        return self.sources

    def random_source(self, nsfw: bool = False) -> str:
        """select a random source from config"""
        source_list = self.sources
        if nsfw:
            # include nsfw sources in random selection
            source_list = source_list + self.nsfw_sources

        return np.random.choice(source_list)


class RouletteSource:
    """
    struct and operations on a source for wallpapers
    """
    SOURCE_TYPES = [
        'REDDIT',
        'INSTAGRAM',
        'URL']

    def __init__(self, source_type: str, url: str) -> None:
        assert source_type in RouletteSource.SOURCE_TYPES
        self.source_type = source_type
        self.source_url = url
        return None

    def random_image(self) -> str:
        """
        Get specific image url from source
        method depends on source type
        """
        if self.source_type == 'REDDIT':
            image_source_url = self._image_from_reddit()
        if self.source_type == 'INSTAGRAM':
            image_source_url = self._image_from_instagram()
        if self.source_type == 'URL':
            image_source_url = self._image_from_direct_url()

        return image_source_url

    def _image_from_reddit(self) -> str:
        """use a URL for a reddit source to select an image"""
        assert self.source_type == 'REDDIT'

        source_url = self.source_url

        header = {
            'User-Agent': 'n00b wallpaper bot v0.4',
            # 'Authorization': 'Client-ID ' + client_id
            }

        req = requests.get(source_url, headers=header)

        # Get json from URL
        json_object = req.json()

        # Get all posts from JSON object
        posts = json_object['data']['children']

        filtered_posts = [p for p in posts if _check_reddit_post(p)]
        if not filtered_posts:
            logging.warning('[source: "%s"]: no usable posts.', self.source_url)
            exit()
        selected_post = np.random.choice(filtered_posts)

        image_url = selected_post['data']['url']

        # logging
        subreddit = selected_post['data']['subreddit']
        name = selected_post['data']['title']
        logging.info('[subreddit: "%s"]: %s', subreddit, name)
        logging.info('[x of %i options]: URL: %s', len(filtered_posts), image_url)

        return image_url

    def _image_from_instagram(self):
        raise NotImplementedError

    def _image_from_direct_url(self):
        raise NotImplementedError

def _check_reddit_post(post):
    """ Return True is reddit post has usable image"""

    # Filter out urls that are not usable images
    suffixes = ['.png', '.jpg']
    has_suffix = lambda url: any([s in url for s in suffixes])

    image_url = post['data']['url']

    if has_suffix(image_url):
        return True
    return False


def run_wallpaper_roulette():
    """run the thing"""
    # Start logging
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        filename=os.path.join(ROOT_PATH, "wallpaper_history.log"),
        level=logging.INFO)

    logging.getLogger("requests").setLevel(logging.WARNING)

    rconf = RouletteConfig()
    source_url = rconf.random_source()
    # hard coded (TODO)
    source_type = 'REDDIT'

    rsrc = RouletteSource(source_type, source_url)
    img_url = rsrc.random_image()

    roulette_image = ImageFetcher()
    roulette_image(source_url=img_url, target_dir='/home/aman/Downloads/')

    # use this for gnome desktop / unity
    setbg_command = ("gsettings set org.gnome.desktop.background picture-uri " +
                     f"file://{roulette_image.dest_path}")
    os.system(setbg_command)

    # use this for i3wm
    setbg_command = f"feh --bg-scale {roulette_image.dest_path}"
    os.system(setbg_command)

    # import subprocess
    # subprocess.call([setbg_command, img_path])

if __name__ == "__main__":
    run_wallpaper_roulette()
