A Wikipedia crawler that finds ~~the meaning of life~~ the list of articles that results
from the process of starting from a given article and following the first wiki article link in the main text,
then repeating the process for subsequent articles, until eventually reaching
the [Philosophy](https://en.wikipedia.org/wiki/Philosophy) article.

It's known that applying this process to most articles in the English Wikipedia eventually leads
to Philosophy (See [Wikipedia:Getting to Philosophy](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy))

## The Rules of the Game

The [Wikipedia article on the subject](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy#Method_summarized) lists the following rules for following links:

1. Clicking on the first non-parenthesized, non-italicized link
2. Ignoring external links, links to the current page, or red links (links to non-existent pages)
3. Stopping when reaching "Philosophy", a page with no links or a page that does not exist, or when a loop occurs

The first rule is not implemented by [api_crawler.py](#api_crawler.py).

Additionally, both [web_crawler.py](#web_crawler.py) and [api_crawler.py](#api_crawler.py)
ignore [namespace pages](https://en.wikipedia.org/wiki/Wikipedia:Namespace#Virtual_namespaces), though this can be changed from [common.py](./common.py).

## Usage

There are two separate implementations of this process in this repo:

- [web_crawler.py](web_crawler.py): a web scraping implementation
- [api_crawler.py](api_crawler.py): an implementation using the [MediaWiki API](https://www.mediawiki.org/wiki/API). This implementation actually follows all article links and not just the first one. There is no way to return links in their article order using the API, as far as I know.

### web_crawler.py

This script provides the `go_to_philosophy` function that returns a list of articles starting from a given title to Philosophy (if there is any path leading there):

```python
>>> from web_crawler import go_to_philosophy

>>> path = go_to_philosophy("Foobar")
>>> print(path)
['Foobar', 'Metasyntactic_variable', 'Placeholder_name', 'Free_variables_and_bound_variables', 'Mathematics', 'Epistemology', 'Ancient_Greek_language', 'Greek_language', 'Indo-European_languages', 'Language_family', 'Language', 'Communication', 'Self', 'Consciousness', 'Sentience', 'Emotion', 'Mental_state', 
'Mind', 'Phenomenon', 'Philosophy']
```

The function accepts an optional `limit` argument to limit the recursion level before giving up.
The default is 1000.

```python
>>> import sys
>>> from web_crawler import go_to_philosophy

# go as far as we can in pursuit of philosophy!
>>> path = go_to_philosophy("Kasiski examination", limit=sys.maxsize)
>>> print(path)
['Kasiski examination', 'Cryptanalysis', 'Information_system', 'Sociotechnical', 'Organizational_development', 'Organizational_change', 'Human_behavior', 'Human', 'Species', 'Biology', 'Science', 'Scientific_method', 'Empirical_evidence', 'Proposition', 'Logic', 'Reason', 'Consciousness', 'Sentience', 'Emotion', 'Mental_state', 'Mind', 'Phenomenon', 'Philosophy']
```

There is also a more general `go_to` function that takes an additional argument for a destination different from Philosophy.

```python
>>> from web_crawler import go_to

>>> path = go_to("Foobar", "Mathematics")
>>> print(path)
['Foobar', 'Metasyntactic_variable', 'Placeholder_name', 'Free_variables_and_bound_variables', 'Mathematics']
```

The scraped pages are cached in the `pages` directory.

### api_crawler.py

This script implements a variant of the problem that follows all article links and not just the first one.
It returns the first path to Philosophy it finds. It also crawls faster due to the use of the API.

```python
>>> from api_crawler import PhilosophyCrawler
>>> philosophy_crawler = PhilosophyCrawler()
>>> path = philosophy_crawler.path_to_philosophy("C (programming language)")
>>> print(path)
['C (programming language)', '"Hello, World!" program', '.deb', 'Deb (file format)', '.NET Framework', '.NET', '.NET Bio', '.NET Foundation', '.NET Compact Framework', 'A Sharp (.NET)', 'Software design', 'Agency (philosophy)', 'Philosophy']
```

The `PhilosophyCrawler` class inherits from the more general `PathToCrawler` and `WikipediaLinkCrawler` classes.
Read the source for more details.

## TODO

- [ ] I've been recently learning about graph databases like Neo4j. Maybe we can do a nice visualization of Wikipedia links like [Six Degrees of Wikipedia](https://www.sixdegreesofwikipedia.com)?

## References

- [Wikipedia:Getting_to_Philosophy#External_links](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy#External_links)

- [loneliness.one/philosophy](https://loneliness.one/philosophy): I used this site to test my implementation. My web crawler script reaches Philosophy from Logic faster due to a bug in that site in handling parenthesized links!
