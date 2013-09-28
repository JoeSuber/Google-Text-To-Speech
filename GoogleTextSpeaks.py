#!/usr/bin/env python
# encoding: utf-8

"""
Thanks and credit for what I, Joe Suber, call GoogleTextSpeaks go to:

A. initial working code, interface to API and great idea -
    Hung Truong (http://www.hung-truong.com/blog/)

B. refinement, refactor, and documentation -
    JulienD, https://github.com/JulienD/Google-Text-To-Speech

C. I added the threadable function call and local cache of .mp3 files
    & re-wrote some french-english documentation into english-english.
    Also added a bit to make it work in Windows.

required audio package:

    sudo apt-get install sox

or really any command line mp3 player, the lighter the better.
I have it working with yauap for gstreamer as well.
and maybe:

    sudo apt-get install libsox-fmt-mp3

example usages:

GoogleTextSpeaks.py -l en -s "I speak to you from outer-space" -p
  - or -
(since there is http action and at least a fraction of a second second delay)
if you want to use it without holding up whatever else is happening,
with a minimum of fuss, call via thread module from your own program:

    import GoogleTextSpeaks as barney
    import thread

    txtraw = 'with the goo goo googly eyes'
    thread.start_new_thread(barney.simplespeech, tuple(txtraw))

# I suppose you can use 'subprocess', but it takes just a tad more to launch & I saw no change.
# GIL or no, most of the action already takes place in a subprocess launched for the .mp3 player
# Each text phrase refers via hash to an on-disk file-name  OR it must be
# retrieved from the Google Translate API - either way
# in a few milli-seconds we are able to send the  .mp3 player
# the name of a closed .mp3 file that exists in directory /voice
# The .mp3 is (already) saved for later use if the phrase comes up again.
# I experimented with a database and keeping files in memory - none of it was worth the trouble
# Just let the OS look up the name of the file. If it ever starts to matter. deal with it then
# It hasn't yet in my app. Even without a file cache it responded in less than a half-second.
# Even if the app has thousands of phrases cached locally for the OS to look through,
# I think the filesystem will always be faster than a call out to the web
# - and you don't bother the Googly web-API as much.

'open the pod-bay doors?'
'would you like to play a game?'
try not to be evil?

-Joe Suber
"""

import argparse
import os
import sys
import re
import urllib, urllib2
import time
import subprocess
from shove import Shove
import psutil
exitFlag = 0

def main():
    """
     cmd line args parsed here, and under last section
    """
    if len(sys.argv)==1:
        # Display the help if no argument is setted.
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.file:
        text = args.file.read()
    if args.string:
        text = ' '.join(map(str,args.string))

    text_lines = convertTextAsLinesOfText(text)
    PLAY = args.play
    downloadAudioFile(text_lines, args.language, args.output)
    play(args.output.name)


def simplespeech(*txtin):
    """
        take a tuple of characters as given by 'thread' call, re-string tuple,
         see if it is an existing file-name and send in the clowns
         If hash collisions ever got to be a problem just run them through a
         new deeper hash algorithm
    """
    txtstr = "".join(txtin)
    txtfixed = convertTextAsLinesOfText(txtstr)
    outfn = os.path.join('voice',  str(hash(txtstr)) + '.mp3')
    if os.path.isfile(outfn):
        play(outfn)
    else:
        with open(outfn, 'wb') as output_f:
            downloadAudioFile(txtfixed, 'en', output_f)
        play(outfn)


def convertTextAsLinesOfText(text):
    """ This converts string or file to a usable chunk or several
        chunks - each smaller than 100 characters.
    """
    # Sanitizes the text.
    text = text.replace('\n','')
    text_list = re.split('(\,|\.|\;|\:)', text)

    # Splits a text into chunks
    text_lines = []
    for idx, val in enumerate(text_list):

        if (idx % 2 == 0):
            text_lines.append(val)
        else :
            # Combines the string + the punctuation.
            joined_text = ''.join((text_lines.pop(),val))

            # Checks if the chunk still needs splitting.
            if len(joined_text) < 100:
                text_lines.append(joined_text)
            else:
                subparts = re.split('( )', joined_text)
                temp_string = ""
                temp_array = []
                for part in subparts:
                    temp_string = temp_string + part
                    if len(temp_string) > 80:
                        temp_array.append(temp_string)
                        temp_string = ""
                #append final part
                temp_array.append(temp_string)
                text_lines.extend(temp_array)

    return text_lines

def downloadAudioFile(text_lines, language, audio_file):
    """
        Donwloads an MP3 from Google Translate.
        *.mp3 content is based on text and language codes parsed
        from commmand line or passed in via simplespeech().
    """
    for idx, line in enumerate(text_lines):
        query_params = {"tl": language, "q": line, "total": len(text_lines), "idx": idx}
        url = "http://translate.google.com/translate_tts?ie=UTF-8" + "&" + unicode_urlencode(query_params)
        headers = {"Host":"translate.google.com", "User-Agent":"Mozilla 5.10"}
        req = urllib2.Request(url, '', headers)
        sys.stdout.write('.')
        sys.stdout.flush()
        if len(line) > 0:
            try:
                response = urllib2.urlopen(req)
                audio_file.write(response.read())
                time.sleep(.3)
            except urllib2.HTTPError as e:
                pass
                #print ('%s' % e)

    #print 'Saved MP3 to %s' % (audio_file.name)
    audio_file.close()


def unicode_urlencode(params):
    """
    Encodes params to be injected into a url.
    """
    if isinstance(params, dict):
        params = params.items()
    return urllib.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])


def play(filename):
    """
    Plays an mp3 depending on the system.
    """
    if sys.platform == "linux" or sys.platform == "linux2":
        # linux
        subprocess.call(["play", filename])
    elif sys.platform == "darwin":
        # OS X
        subprocess.call(["afplay", filename])
        # only 32 bit windows, but a lot of win x86_64
        # py installs are 32bit. Too much work for _64 fix
    elif sys.platform == 'win32':
        print ("trying windows default")
        subprocess.call(["WMPlayer", filename])


if __name__ == '__main__':

    description = "Google Text To Speech."
    parser = argparse.ArgumentParser(prog='GoogleTextSpeaks', description=description,
                                     epilog='have fun')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=argparse.FileType('r'), help='File to read text from.')
    group.add_argument('-s', '--string', action='store', nargs='+', help='A string of text to convert to speech.')

    parser.add_argument('-o','--output', action='store', nargs='?',
                        help='Filename to output audio to',
                        type=argparse.FileType('w'),
                        default='out.mp3')
    parser.add_argument('-l','--language', action='store', nargs='?', help='Language to output text to.', default='en')

    parser.add_argument('-p','--play', action='store_true', help='Play the speech if your computer allows it.')
    #parser.add_argument('-c','--cache', action='store_true', help='Cache the result of the file for a later use.')

    main()
