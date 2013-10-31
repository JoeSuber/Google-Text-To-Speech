#!/usr/bin/env python
# encoding: utf-8

"""
10-31-13
Latest update!
- The command line-given phrases and text files now cache properly.
 - You can have this thing record a Tolstoy novel if you want.
- Some small but annoying punctuation & spacing bugs have been squashed.
- If using a text file for input it still must have some punctuation.
- The threaded calls no longer burp text all over stdout
****
check README for pre-reqs, sample usages & credits
***
-Joe Suber
"""

import argparse
import os
import sys
import re
import urllib, urllib2
import time
import subprocess
exitFlag = 0

def main(p='nope', exists=False):
    """
     cmd line args parsed here, and under __name__==__main__
    """
    if len(sys.argv) == 1:
        # Display the help if no argument is set.
        parser.print_help()
        sys.exit(1)

    if exists:
        #print('shortcut taken!')
        play(p)
    else:
        args = parser.parse_args()

        if args.file:
            text = args.file.read()
            #print('reading from {}'.format(args.file))
            #print('writing to   {}'.format(args.output.name))
        if args.string:
            text = ''.join(map(str, args.string))

        text_lines = convertTextAsLinesOfText(text)
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
    text = text.replace('\n', ' ')
    text_list = re.split('(\,|\.|\;|\:)', text)

    # Splits a text into chunks
    text_lines = []
    for idx, val in enumerate(text_list):

        if idx % 2 == 0:
            text_lines.append(val)
        else:
            # Combines the string + the punctuation.
            joined_text = ''.join((text_lines.pop(), val))

            # Checks if the chunk still needs splitting.
            if len(joined_text) < 100:
                text_lines.append(joined_text)
            else:
                subparts = re.split('( )', joined_text)
                temp_string = ""
                temp_array = []
                for part in subparts:
                    temp_string += part
                    if len(temp_string) > 80:
                        temp_array.append(temp_string)
                        temp_string = ""
                #append final part
                temp_array.append(temp_string)
                text_lines.extend(temp_array)

    return text_lines


def downloadAudioFile(text_lines, language, audio_file):
    """
        Downloads an MP3 from Google Translate.
        *.mp3 content is based on text and language codes parsed
        from command line or passed in via simplespeech().
    """
    # print(text_lines, language, audio_file)
    for idx, line in enumerate(text_lines):
        query_params = {"tl": language, "q": line, "total": len(text_lines), "idx": idx}
        url = "http://translate.google.com/translate_tts?ie=UTF-8" + "&" + unicode_urlencode(query_params)
        headers = {"Host": "translate.google.com", "User-Agent": "Mozilla 5.10"}
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
                print ('ER %s' % e)
    # for really textless operation comment out below
    print 'Saved MP3 to %s' % audio_file.name
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
        subprocess.call(["play", '-q', filename])
    elif sys.platform == "darwin":
        # OS X
        subprocess.call(["afplay", filename])
        # only 32 bit windows, but a lot of win x86_64
        # py installs are 32bit. Too much work for _64 fix
    elif sys.platform == 'win32':
        print ("trying windows default")
        subprocess.call(["WMPlayer", filename])


if __name__ == '__main__':

    description = "Google Text To Speech"
    parser = argparse.ArgumentParser(prog='GoogleTextSpeaks', description=description,
                                     epilog='there once was a man from nantucket...')

    parser.add_argument('-l', '--language', action='store', nargs='?', help='Language to output text to', default='en')

    parser.add_argument('-p', '--play', action='store_true', help='Play the speech if your computer allows it')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=argparse.FileType('r'), help='File to read text from.')
    group.add_argument('-s', '--string', action='store', nargs='+', help='A string of text to convert to speech.')

    chosen = parser.parse_args()
    if chosen.file:
        mtext = chosen.file.read()
        #print(mtext)
    else:
        mtext = chosen.string
    #print('mtext = '.format(mtext[0]))
    pathname = os.path.join('voice',  str(hash("".join(mtext))) + '.mp3')
    #print('hash-made path for parser gen. fob = {}'.format(pathname))
    parser.add_argument('-o', '--output', action='store', nargs='?',
                        help='Filename to output audio to',
                        type=argparse.FileType('w'),
                        default=pathname)

    main(p=pathname, exists=(os.path.isfile(pathname) and (os.stat(pathname).st_size > 1)))
