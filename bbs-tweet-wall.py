#####################################################################################
#
# BBS TWEET WALL by Alpha
# CORPORATION X BBS // corpxbbs.com:2323
# robbiew@gmail.com
# github:
#
# BBS Tweet Wall returns 3 random tweets from 3 Twitter lists.
#
# Define your lists and pther settings in bbs-tweet-wall.cfg
#
# Uses Tweepy, a python library for accessing Twitter's API
# https://www.tweepy.org/
#
# IMPORTANT! You MUST apply for a Twitter dev account, create an app and get auth keys.
# https://developer.twitter.com/en/apply-for-access
#
# Next, create an "auth.cfg" file that looks like this:
#
# [auth]
# auth_key: rzfBFE92u2HCZIYs8rABO87YM
# auth_secret:VUKqHesLLtbwxk76KC9NroSmJvHdUcHKZuzCg5lsT5uOZtsUQD
#
# Install python libraries:
#   "sudo apt-get python3"
#   "sudo apt install python3-pip"
#   "pip3 install tweepy"
#   "pip3 install unidecode"
#
# Run this script as a cron event, or using a BBS event (e.g. at login).
#
# Output file will be "tweets-all.ans" (or .asc, .msg, etc.)
#
# Tested on Python 3, linux 64 (Ubuntu 20.04) only
# This may/probably work on Windows with a little elbow grease.
# Have fun!
#
#######################################################################################

import tweepy
import sys
import glob
import os
import configparser as ConfigParser
from textwrap import fill
import textwrap
from unidecode import unidecode
import time
import random
import timeago
import datetime

# main config file
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(
    __file__)) + '/bbs-tweet-wall.cfg')

# Twitter auth key (I like to keep seperate)
auth = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(
    __file__)) + '/auth.cfg')

# get Twitter auth values from config
auth_key = config.get('auth', 'auth_key')
auth_secret = config.get('auth', 'auth_secret')

# setup Twtter oauth2 with values
auth = tweepy.AppAuthHandler(auth_key, auth_secret)
api = tweepy.API(auth)

# Get Twitter list count from config file, make it an integer
list_count = config.get('config', 'list_count')
list_count_int = int(list_count)

# Get format parameters from config
tweet_max = int(config.get('config', 'tweet_max'))
tweet_width = int(config.get('config', 'tweet_width'))
tweet_lines = int(config.get('config', 'tweet_lines'))
file_ext = config.get('config', 'file_ext')
output_dir = config.get('config', 'output_dir')
bgFileName = config.get('config', 'bgFileName')
output_file = output_dir + '/' + 'tweets-all.' + file_ext
textFile = open(output_file, 'w+', encoding='cp437', errors='replace')


def start():
    f = open(bgFileName, 'r', encoding='cp437')
    contents = f.read()
    textFile.write(contents)
    print("Writing background art file...")


def get_list():
    count_lists = list_count_int
    while count_lists > 0:
        count_lists -= 1
        list_id_str = str(count_lists)
        current_list = config.get('config', 'list_' + list_id_str + '_id')
        list_tweets(current_list, list_id_str)

# We grab all the user_names in each list, but we only display one from each list,
# so we randomize each time, and return that name only, for variety..


def random_name(screen_names):
    newlist = []
    newlist.append(screen_names[0])
    print(newlist)
    return newlist


# Get the latest tweets for each member in each List
def list_tweets(current_list, list_id_str):
    screen_names = []
    # returns members of a list & some details on them
    for user in tweepy.Cursor(api.list_members, list_id=current_list, owner_screen_name="robbiew", include_entities=True).items():
        screen_names.append(f"{user.screen_name}")
    random.shuffle(screen_names)
    name = random_name(screen_names)
    for i in name:

        # returns TWEET_MAX tweets from a user: always 1 for now
        # ADD: pagination for multiple tweet screens
        for status in tweepy.Cursor(api.user_timeline, screen_name=i, tweet_mode="extended", count=tweet_max).items(tweet_max):
            side = list_id_str
            name_color = config.get(
                'config', 'list_' + list_id_str + '_name_color')
            footer_color = config.get(
                'config', 'list_' + list_id_str + '_footer_color')
            date_color = config.get(
                'config', 'date_color')

            favs = footer_color + f"+ favorited: {status.favorite_count}"
            rts = footer_color + f"+ retweeted: {status.retweet_count}"
            # followers = footer_color + \
            #     f"+ followers: {status.user.followers_count}"

            screen_name = name_color + f"@{status.user.screen_name}"
            screen_name_wrap = textwrap.fill(
                unidecode(screen_name), width=tweet_width)

            tweet_body = f"{status.full_text}"
            body_wrap = textwrap.fill(
                unidecode(tweet_body), width=tweet_width,  max_lines=tweet_lines)

            tweet_date = f"{status.created_at}"

            time = pretty_date(tweet_date)

            # Save each tweet name + body to a temp file (e.g "tweet0.")
            # ADD: write from memory to skip tjos
            tweet_file = 'tweets_' + side + '.ans'
            textFile_tweet = open(tweet_file, 'w+',
                                  encoding='cp437', errors='replace')

            textFile_tweet.write(screen_name_wrap)
            textFile_tweet.write("\n\n|16|15\n")
            textFile_tweet.write(body_wrap)
            textFile_tweet.close()

            # Need XY cordinates to write the text into columns
            x_date = config.get('config', 'list_pos_x_date')
            x_body = config.get('config', 'list_pos_x')
            x_favs = config.get('config', 'list_pos_x_favs')
            x_rts = config.get('config', 'list_pos_x_rts')
            # x_followers = config.get('config', 'list_pos_x_followers')
            y = config.get('config', 'list_' + list_id_str + '_pos_y')

            # Send content off to the write function
            write_tweet_body(int(x_body), int(y), tweet_file)
            write_footer(int(x_date), int(y), date_color + time, 0)
            write_footer(int(x_favs), int(y), favs, 0)
            write_footer(int(x_rts), int(y), rts, 0)
            # write_footer(int(x_followers), int(y), followers, 0)

# Write out starting at X coord. and increment for each line


def write_tweet_body(x_body, y, tweet_file):
    infile = open(tweet_file).readlines()
    x = (x_body - 1)
    for line in infile:
        x += 1
        textFile.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, line))


# We write the footer content line by line, so no need to increment here
def write_footer(x_footer, y, footer, offset):
    y_adjust = y+offset
    textFile.write("\x1b7\x1b[%d;%df%s\x1b8" % (x_footer, y_adjust, footer))


def pretty_date(time):
    date = time
    pretty_date = (timeago.format(date))

    print(pretty_date)
    return pretty_date


# tidy up!
def end():
    textFile.close()
    # print("Removing *.tmp files...")
    # for f in glob.glob(output_dir + "/*.tmp"):
    #     os.remove(f)
    # print("Done! Created: " + output_file)


def main():
    start()
    get_list()
    end()


if __name__ == '__main__':
    main()
