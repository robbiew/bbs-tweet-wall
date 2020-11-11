#####################################################################################
#
# BBS TWEET WALL by Alpha
# CORPORATION X BBS // corpxbbs.com:2323
# robbiew@gmail.com
# github: https://github.com/robbiew/bbs-tweet-wall
#
# BBS Tweet Wall returns 3 random tweets from 3 defined Twitter lists.
#
# Define your lists and other settings in bbs-tweet-wall.cfg
#
# Uses Tweepy, a python library for accessing Twitter's API
# https://www.tweepy.org/
#
# IMPORTANT! You MUST apply for a Twitter dev account, create an app and get auth keys.
# https://developer.twitter.com/en/apply-for-access
#
# Next, create an "auth.cfg" file that looks like this (replace with your own):
#
# [auth]
# auth_key: xxxxx
# auth_secret: xxxxx
#
# Then, install python3 & python libraries:
#   "sudo apt install python3"
#   "sudo apt install python3-pip"
#   "pip3 install tweepy unidecode timeago colorama "
#
# Run this script as a cron event, or using a BBS event (e.g. at login).
#
# Output file will be "tweets-all.ans" (or .asc, .msg, etc.) in output_dir.
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
import random
import timeago
from colorama import init, Fore, Back, Style

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
script_dir = config.get('config', 'script_dir')
bgFileName = config.get('config', 'bgFileName')
output_file = output_dir + '/' + 'tweets-all.' + file_ext
textFile = open(script_dir + '/tweets.tmp', 'w+',
                encoding='cp437', errors='replace')

# Here we go!


def start():
    # use Colorama to make Termcolor work on Windows too
    init()
    # open our background art and save as background
    f = open(script_dir + "/" + bgFileName, 'r', encoding='cp437')
    contents = f.read()
    textFile.write(contents)

# Get Twitter list data


def get_list():
    count_lists = list_count_int
    while count_lists > 0:
        count_lists -= 1
        list_id_str = str(count_lists)
        current_list = config.get('config', 'list_' + list_id_str + '_id')
        list_tweets(current_list, list_id_str)


# Randomize Lists and grab the first user name, we only need 1 tweet per side
def list_tweets(current_list, list_id_str):
    screen_names = []
    # returns members of a list & some details on them
    for user in tweepy.Cursor(api.list_members, list_id=current_list, owner_screen_name="robbiew", include_entities=True).items():
        screen_names.append(f"{user.screen_name}")

    random.shuffle(screen_names)
    print(screen_names[0])

    tweets_by_name(screen_names[0], list_id_str)


# Get latest twitter statuses for each side/name
def tweets_by_name(name, list_id_str):
    statuses = tweepy.Cursor(api.user_timeline, screen_name=name,
                             tweet_mode="extended", count=tweet_max).items(tweet_max)
    for status in statuses:
        side = list_id_str

        # can't save a Colorama variable as a config variable, so define here
        # TODO: move these values to bbs-tweet-wall.cfg
        if side == "0":
            name_fg_color = Fore.YELLOW
            name_bg_color = Back.BLUE
            name_style = Style.BRIGHT

            date_fg_color = Fore.CYAN
            date_bg_color = Back.BLUE
            date_style = Style.BRIGHT

            body_fg_color = Fore.BLUE
            body_bg_color = Back.BLACK
            body_style = Style.BRIGHT

            footer_fg_color = Fore.BLUE
            footer_bg_color = Back.BLUE
            footer_style = Style.BRIGHT

        if side == "1":
            name_fg_color = Fore.YELLOW
            name_bg_color = Back.RED
            name_style = Style.BRIGHT

            date_fg_color = Fore.CYAN
            date_bg_color = Back.RED
            date_style = Style.BRIGHT

            body_fg_color = Fore.RED
            body_bg_color = Back.BLACK
            body_style = Style.BRIGHT

            footer_fg_color = Fore.RED
            footer_bg_color = Back.RED
            footer_style = Style.BRIGHT

        # Data we'll need from the twitter api
        screen_name = name
        tweet_date = f"{status.created_at}"
        time = pretty_date(tweet_date)
        tweet_body = f"{status.full_text}"
        favs = f"+ favorited: {status.favorite_count}"
        rts = f"+ retweeted: {status.retweet_count}"

        # followers = footer_color + \
        #     f"+ followers: {status.user.followers_count}"

        # Deal with wierd/garbage characters
        screen_name_wrap = textwrap.fill(
            unidecode(screen_name), width=tweet_width)
        time_wrap = textwrap.fill(
            unidecode(time), width=tweet_width)
        body_wrap = textwrap.fill(
            unidecode(tweet_body), width=tweet_width,  max_lines=tweet_lines)
        favs_wrap = textwrap.fill(
            unidecode(favs), width=tweet_width)

        # Get XY cordinates so we can write the text into columns
        x_date = config.get('config', 'list_pos_x_date')
        x_name = config.get('config', 'list_pos_x_name')
        x_body = config.get('config', 'list_pos_x_body')
        x_favs = config.get('config', 'list_pos_x_favs')
        x_rts = config.get('config', 'list_pos_x_rts')
        y = config.get('config', 'list_' + list_id_str + '_pos_y')
        # x_followers = config.get('config', 'list_pos_x_followers')

        # Save each tweet name + body to a temp file (e.g "tweet0.tmp")
        # TODO: save in memory/as an object
        tweet_file = script_dir + '/tweets_' + side + '.tmp'
        textFile_tweet = open(tweet_file, 'w+',
                              encoding='cp437', errors='replace')

        textFile_tweet.write(
            body_bg_color + body_fg_color + body_bg_color + body_style + body_wrap)
        textFile_tweet.close()

        # Send content off to the write function
        write_tweet_name(int(x_name), int(y), name_bg_color +
                         name_fg_color + name_style + '@' + screen_name_wrap)

        write_footer(int(x_date), int(y), date_bg_color +
                     date_fg_color + date_style + time_wrap, 0)

        write_tweet_body(int(x_body), int(y), tweet_file)

        write_footer(int(x_favs), int(y), footer_fg_color +
                     footer_bg_color + footer_style + favs_wrap, 0)
        write_footer(int(x_rts), int(y), rts, 0)
        # write_footer(int(x_followers), int(y), followers, 0)


# Write out Twitter User Name at XY coordinates
def write_tweet_name(x_name, y, text):
    textFile.write("\x1b7\x1b[%d;%df%s\x1b8" % (x_name, y,  text))


# Write out body starting at XY coord. and then increment for each line
# This produces some garbage escape sequences that we'll deal with later
# TODO: Read from memory. not a file
def write_tweet_body(x_body, y, tweet_file):
    infile = open(tweet_file).readlines()
    x = (x_body - 1)
    for line in infile:
        x += 1
        textFile.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, line))
    print(infile)


# Write each footer item, line by line
def write_footer(x_footer, y, footer, offset):
    y_adjust = y+offset
    textFile.write("\x1b7\x1b[%d;%df%s\x1b8" % (x_footer, y_adjust, footer))

# Return dates as friendly "time ago" vs. UTC date stamp


def pretty_date(time):
    date = time
    pretty_date = (timeago.format(date))
    return pretty_date


# tidy up!
# remove some garbage escape sequences mucking up the output
# delete temp files
# TODO: write from memory, don't write/delete temp files!
def end():
    textFile.close()

    with open(script_dir + '/tweets.tmp', 'r', encoding='cp437') as infile, \
            open(output_file, 'w', encoding='cp437') as outfile:
        data = infile.read()
        data = data.replace("7", "")
        data = data.replace("8", "")
        outfile.write(data)

    print("Removing *.tmp files...")
    for f in glob.glob(script_dir + "/*.tmp"):
        os.remove(f)
    print("Done! Created: " + output_file)


def main():
    start()
    get_list()
    end()


if __name__ == '__main__':
    main()
