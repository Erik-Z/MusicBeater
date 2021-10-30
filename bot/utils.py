import urllib.request
import json
import urllib
import pprint
import re


def get_title_from_yt_url(vid_url):
    params = {"format": "json", "url": vid_url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string
    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        # pprint.pprint(data)
        return data['title']


def get_url_from_title(title: str):
    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}")
    urls = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return urls[0]