Google-Text-To-Speech
=====================
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

 I suppose you can use 'subprocess', but it takes just a tad more to launch & I saw no change.
 GIL or no, most of the action already takes place in a subprocess launched for the .mp3 player
 Each text phrase refers via hash to an on-disk file-name OR it must be
 retrieved from the Google Translate API - either way
 in a few milli-seconds we are able to send the .mp3 player
 the name of a closed .mp3 file that exists in directory /voice
 The .mp3 is (already) saved for later use if the phrase comes up again.
 I experimented with a database and keeping files in memory - none of it was worth the trouble
 Just let the OS look up the name of the file. If it ever starts to matter. deal with it then
 It hasn't yet in my app. Even without a file cache it responded in less than a half-second.
 Even if the app has thousands of phrases cached locally for the OS to look through,
 I think the filesystem will always be faster than a call out to the web
# - and you don't bother the Googly web-API as much.

'open the pod-bay doors?'
'would you like to play a game?'
try not to be evil?

-Joe Suber
"""

