#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script redirect a bbc video url to the original video file
so it can be downloaded easily.
"""

from __future__ import print_function

__author__ = "Alexandre Chassany"
__copyright__ = "Copyright 2014, Alexandre Chassany"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Alexandre Chassany"
__email__ = "alexandre.chassany@gmail.com"
__status__ = "Prototype"

import argparse
import sys
import urllib2
import urlparse
import webbrowser
from xml.dom import minidom

class MyArgParser(argparse.ArgumentParser):
    def error(self, message):
        print('error: {0}'.format(message), file=sys.stderr)
        print('', file=sys.stderr)
        self.print_help()
        sys.exit(2)

def _main(argv):
    # parser = MyArgParser(description=\
    #                                  'Redirect a bbc video url to the url of the ' \
    #                                  'original video file so it can be downloaded easily.')
    # parser.add_argument('url', help='Url to the bbc video you want to download' \
    #                     '(example: http://www.bbc.com/news/world-europe-27926482)')

    # args = parser.parse_args(argv)
    # url = args.url

    url = raw_input('Enter the video url (Press Enter to validate): ')
    
    # Get the path of the url
    parsed_url = list(urlparse.urlsplit(url))
    
    # Build playlist url
    parsed_url[1] = 'playlists.bbc.co.uk'
    parsed_url[2] += 'A/playlist.sxml'

    playlist_page = urllib2.urlopen(urlparse.urlunsplit(parsed_url)).read()
    playlist_xml_doc = minidom.parseString(playlist_page)
    group = ''
    for item in playlist_xml_doc.getElementsByTagName('item'):
        if item.attributes['kind'].value == 'programme':
            group = item.attributes['group'].value

    if not group:
        raise Exception("Couldn't determine the group of the video!.")

    mediaselector_url = ('http', 'open.live.bbc.co.uk',
                         'mediaselector/5/select/version/2.0/mediaset/journalism-pc/vpid/{0}'.format(group),
                         '','')
    mediaselector_page = urllib2.urlopen(urlparse.urlunsplit(mediaselector_url)).read()
    mediaselector_xml_doc = minidom.parseString(mediaselector_page)
    
    best_bit_rate = 0
    media_element = None
    for media in mediaselector_xml_doc.getElementsByTagName('media'):
        bit_rate = int(media.attributes['bitrate'].value)
        if bit_rate > best_bit_rate:
            media_element = media
            best_bit_rate = bit_rate

    if not media:
        raise Exception("Couldn't find any suitable media!")

    video_identifier = media_element.getElementsByTagName('connection')[0].attributes['identifier'].value
    video_identifier = video_identifier.split(':')[-1]
    video_identifier = '/'.join(video_identifier.split('/')[1:])

    video_url = urlparse.urlunsplit(('http', 'news.downloads.bbc.co.uk.edgesuite.net',
                         video_identifier, '', ''))

    webbrowser.open(video_url, new=2)

    raw_input('Check your new browser web tab to download your video (Press Enter to Finish)')
        

if __name__ == '__main__':
    try:
        _main(sys.argv[1:])
    except Exception as e:
        print(e)
        print('An error occured. Please contact {0} at {1}'.format(__author__, __email__))
        raw_input('Press Enter to continue')
    
