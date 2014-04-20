"""
Read and write RSS entries for dripfed comics. The design ideal is to use the RSS format itself as the entire data
store: nothing outside the RSS file needs to keep track of earlier entries that have already been written. That means
we need to be able to round-trip an RSS file: parse it to python objects, manipulate those objects (adding an entry,
possibly removing any error entries there might be) and generate a new RSS feed for the new content. There doesn't seem
to be a library that handles *both* ends of this, funnily enough.
"""
from datetime import datetime
import feedparser as rss_parse
import PyRSS2Gen as rss_gen

__author__ = 'tikitu'


def parse_rss(fp):
    parsed = rss_parse.parse(fp)

    to_gen = rss_gen.RSS2(
        title=parsed['feed']['title'],
        link=parsed['feed']['link'],
        description=parsed['feed']['description'],
        lastBuildDate=struct_time_to_datetime(parsed['feed']['updated_parsed']),
        items=[
            rss_gen.RSSItem(
                title=entry['title'],
                link=entry.get('link'),
                description=entry['summary'],
                pubDate=struct_time_to_datetime(entry['published_parsed']),
            )
            for entry in parsed['entries']
        ]
    )
    return to_gen


def add_entry(rss, config):
    while rss.items and rss.items[0].title.endswith('error'):
        rss.items.pop(0)
    rss.items[0:0] = [
        rss_gen.RSSItem(
            title='New {0} episode'.format(config.comic.full_name),
            description='Episode {0} provided by dripfeed'.format(config.episode),
            link=config.next_url,
            pubDate=datetime.now()
        )
    ]


def add_error_entry(rss, exception):
    rss.items[0:0] = [
        rss_gen.RSSItem(
            title='Latest episode has an error',
            description=unicode(exception),
            pubDate=datetime.now(),
        )
    ]


def init_rss(config):
    rss = rss_gen.RSS2(
        title='Dripfeed for {0}'.format(config.comic.full_name),
        link='file://{0}'.format(config.rss_file),
        description='Dripfeed replays comic archives at the rate you choose',
        lastBuildDate=datetime.now()
    )
    with open(config.rss_file, 'w+') as f:
        rss.write_xml(f)
        f.truncate()



def struct_time_to_datetime(struct_time):
    return datetime(*struct_time[:6])