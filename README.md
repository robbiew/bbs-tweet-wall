# bbs-tweet-wall
Python script that creates an ANSI file using Twitter lists.
Returns 3 random tweets from 3 defined Twitter lists.
Use this as a BBS logon or logoff screen? <shrugs>

Define your lists and other settings in bbs-tweet-wall.cfg.
Uses Tweepy, a python library for accessing Twitter's API: https://www.tweepy.org/
IMPORTANT! You MUST apply for a Twitter dev account, create an app and get auth keys: https://developer.twitter.com/en/apply-for-access

SETUP

1. create an "auth.cfg" file that looks like this (replace with your own):

[auth]
auth_key: xxxxx
auth_secret: xxxxx

2. Then, install python3 & python libraries:
  "sudo apt install python3" 
  "sudo apt install python3-pip"
  "pip3 install tweepy unidecode timeago colorama "

3. Run this script as a cron event, or using a BBS event (e.g. at login).

Output file will be "tweets-all.ans" (or .asc, .msg, etc.) in output_dir.

Tested on Python 3, linux 64 (Ubuntu 20.04) only... This may/probably work on Windows with a little elbow grease.

Have fun!

