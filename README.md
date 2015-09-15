# Wallpaper roulette


## Description
Sets my Ubuntu desktop wallpaper to a random image (e.g from reddit
subreddits). This is a simple script to which I've added some slight 
improvements over time: 
  - choose which subreddits from which to grab images
  - simple logging of images used
  - some error checks
  - command line arguments
  - NSFW mode (separate list of subreddit sources that are less reliable to use
    at work)
  - Sources stored in YAML file

## Command line execution

```
usage: set_wallpaper.py [-h] [--nsfw]

optional arguments:
  -h, --help  show this help message and exit
  --nsfw      get image from alternate list of sources
```

## Scheduling

I've set up a cronjob to run this script every 60 minutes. It fails silently,
in case my computer is without internet or behind a firewall. 

 * uses os.system to execute the command
 * can still be executed manually anytime
 * create cronjob: `$ crontab -u`
 * troublshoot cronjob: `$ tail /var/log/syslog | grep crontab`


## Disclaimer!

 This script was created for my personal use and entertainment only. 
 Images on reddit may not be appropriate for your boss, the child 
 sitting behind you at the cafe, or for you. This script may violate 
 some internet access or provider EULAs. 

