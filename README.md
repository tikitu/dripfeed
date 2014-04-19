Simultaneously:

* a commandline utility to create RSS feeds of webcomic archives, "drip feeding" entries at intervals to avoid binging; and
* an excuse to play with some tools I haven't used yet. So far:
    - [`cookiecutter`](https://github.com/audreyr/cookiecutter) (fill out a multi-file template for new projects)
    - [`docopt`](http://docopt.org/) (commandline arg parsing)
    - [`scrapy`](http://scrapy.org/) (web spiders; turns out is *massive* overkill for what we need)
    - [`BeautifulSoup`](http://www.crummy.com/software/BeautifulSoup/) (html parsing; turns out not well-suited to
      abstracting over the path to find the "next" url: paths are chained Python attribute lookups, not easily
      manipulable)
    - [`lxml`](http://lxml.de/) (allows XPath expressions, simple Python strings so perfect for abstraction)

