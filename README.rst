===============================
dripfeed
===============================

.. image:: https://travis-ci.org/tikitu/dripfeed.png?branch=master
        :target: https://travis-ci.org/tikitu/dripfeed

.. image:: https://pypip.in/d/dripfeed/badge.png
        :target: https://crate.io/packages/dripfeed?version=latest


Create an RSS feed of a webcomic archive, for slow catchup.

Ever time I discover a new webcomic that's worth following, I lose hours (often night-time hours) to catching up with
the archives. This tool exists to avoid this problem: I can create my own dripfeed for the comic, schedule it with cron
to update two or three times a day, and add the feed to my ordinary feed reader. So long as ``dripfeed`` updates more
often than the comic author, my dripfeed will catch up eventually, and I can switch to the official feed from then on.

Example usage
-------------

Create the feed::

    dripfeed init gunnerkrigg  # name for dripfeed commands like "update", "remove" (commandline-friendly)
                  --rss ./gunnerkrigg.rss  # rss file for output (will be created)
                  --url 'http://gunnerkrigg.com/?p=1'  # where to find the first page
                  --next "//img[@src='http://www.gunnerkrigg.com/images/next_a.jpg']/.."  # XPath for "next" link
                  --name 'Gunnerkrigg Court'  # optional long name for output (doesn't have to be commandline-friendly)

The ``--next`` parameter is an XPath expression that extracts the ``<a>`` element whose ``href`` points to the next page.
(This expression will be used for all pages of the comic.)

This places configuration for ``gunnerkrigg`` in a config file at ``~/.dripfeed.cfg`` (creating the file if it doesn't
already exist).

Now running::

    dripfeed update gunnerkrigg

will update the rss feed at ``./gunnerkrigg.rss`` and store progress in ``~/.dripfeed.cfg``: I'd expect this command to
go in a cron job.

Errors are recorded in the RSS feed, and you can run ``dripfeed update`` with a ``--debug`` flag to see a full stack
trace of the error.

Output
------

The RSS feed entries are intentionally very very simple: they contain just a link to the page, and some placeholder text
telling you which episode you're looking at (counting from episode 1 at the initial URL).

It would be possible to extend the tool to include some degree of content scraping: more XPath expressions could
optionally extract the comic image, title, commentary, etc. I *do not* intend to do this; of course you're welcome to
fork the code and make whatever changes you like, but I will not accept pull requests adding these features. The reason
is that I want you to visit the original comic pages: making a living from webcomics is tricky enough as it is, and
many comics are either directly or indirectly ad-supported. This script is not a syndication tool and is emphatically
not intended to make business any harder for the authors whose work I admire.

Requirements
------------

- Python >= 2.6

License
-------

MIT licensed. See the bundled `LICENSE <https://bitbucket.org/tikitu/dripfeed/src/tip/dripfeed/LICENSE>`_ file for more details.

TODO
----

Not sure when I'll get around to these, but here are a couple things I would like to do with it (maybe more for
the learning experience than because the task really demands it):

* Interactive ``init`` that prompts for necessary args and validates them (especially the xpath).
* Example config file pushing my favourite webcomics.
