import json
from pathlib import Path
import sys
from typing import Dict, List, Optional, Set

import requests

import common


class WikipediaLinkCrawler:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "pllimit": "max",
    }

    def __init__(self, cache_file: Optional[str] = None):
        self.session = requests.Session()
        self.cache_file = cache_file
        if cache_file:
            self._read_cache(Path(cache_file))

    def close(self) -> None:
        if self.cache_file:
            with open(self.cache_file, "w", encoding="utf-8") as file:
                json.dump(self.cache, file)

    def _read_cache(self, cache_file: Path):
        if not cache_file.exists():
            cache_file.write_text("{}", encoding="utf-8")
        with open(cache_file, encoding="utf-8") as file:
            self.cache = json.load(file)

    def get_cached_links(self, title: str) -> List[str]:
        return self.cache.get(title, [])

    def write_cached_links(self, title: str, links: List[str]):
        self.cache[title] = links

    def should_include_title(self, title: str):
        return not common.is_namespace_title(title)

    # adapted from https://stackoverflow.com/a/57983365
    def get_linked_titles(self, title: str) -> List[str]:
        def add_links(links: List[str], pages: Dict[str, Dict]):
            for page in pages.values():
                if "missing" in page:
                    continue
                for link in page["links"]:
                    if self.should_include_title(link["title"]):
                        links.append(link["title"])

        links = self.get_cached_links(title)
        if links:
            return links
        params = {**self.params, "titles": title}
        response = self.session.get(url=self.url, params=params)
        data = response.json()
        pages = data["query"]["pages"]
        add_links(links, pages)
        while "continue" in data:
            plcontinue = data["continue"]["plcontinue"]
            params["plcontinue"] = plcontinue
            response = self.session.get(url=self.url, params=params)
            data = response.json()
            pages = data["query"]["pages"]
            add_links(links, pages)
        self.write_cached_links(title, links)

        return links


class PathToCrawler(WikipediaLinkCrawler):
    def _crawl(
        self,
        path: List[str],
        visited: Set[str],
        origin_title: str,
        target_title: str,
        limit: int,
        depth: int = 0,
    ) -> bool:
        print(f'crawling "{origin_title}"', file=sys.stderr)
        if origin_title == target_title:
            return True
        elif origin_title in visited:
            return False
        visited.add(origin_title)
        if depth + 1 > limit:
            return False
        titles = self.get_linked_titles(origin_title)
        for linked_title in titles:
            if self._crawl(
                path, visited, linked_title, target_title, limit, depth=depth + 1
            ):
                path.append(linked_title)
                return True
        return False

    def path_to(self, origin_title: str, target_title: str, limit=12) -> List[str]:
        path: List[str] = []
        visited: Set[str] = set()
        success = self._crawl(path, visited, origin_title, target_title, limit)
        if success:
            path.append(origin_title)
        path.reverse()
        return path


class PhilosophyCrawler(PathToCrawler):
    def path_to_philosophy(self, origin_title: str, limit=12) -> List[str]:
        return self.path_to(origin_title, "Philosophy", limit)


if __name__ == "__main__":
    titles = [
        "Wikipedia:Getting_to_Philosophy",
        "Foobar",
        "C (programming language)",
        # "Albert Einstein",
        # "Logic",
        # "Philosophy",
        # "Wikipedia",
    ]
    try:
        philosophy_crawler = PhilosophyCrawler("cached_links.json")
        for title in titles:
            path = philosophy_crawler.path_to_philosophy(title)
            print(path)
    finally:
        philosophy_crawler.close()
