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


def add_entry(rss, comic, num_entries=20):
    while rss.items and rss.items[0].title.endswith('error'):
        rss.items.pop(0)
    rss.items[0:0] = [
        rss_gen.RSSItem(
            title='New {0} episode'.format(comic.full_name),
            description='Episode {0} provided by dripfeed'.format(comic.progress.episode),
            link=comic.progress.next_url,
            pubDate=datetime.utcnow()
        )
    ]
    rss.items = rss.items[:num_entries]


def add_error_entry(rss, exception, num_entries=20):
    rss.items[0:0] = [
        rss_gen.RSSItem(
            title='Latest episode has an error',
            description=unicode(exception),
            pubDate=datetime.utcnow(),
        )
    ]
    rss.items = rss.items[:num_entries]


def init_rss(comic):
    now = datetime.utcnow()
    rss = rss_gen.RSS2(
        title='Dripfeed for {0}'.format(comic.full_name),
        link='file://{0}'.format(comic.rss_file),
        description='Dripfeed replays comic archives at the rate you choose',
        lastBuildDate=now,
        items=[
            rss_gen.RSSItem(
                title='First {0} episode'.format(comic.full_name),
                description='Episode 1 provided by dripfeed',
                link=comic.start_url,
                pubDate=now,
            )
        ]
    )
    with open(comic.rss_file, 'w+') as f:
        rss.write_xml(f)
        f.truncate()


def struct_time_to_datetime(struct_time):
    return datetime(*struct_time[:6])