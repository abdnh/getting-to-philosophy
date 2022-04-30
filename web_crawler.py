import itertools
from pathlib import Path
import re
import sys
from typing import List, Set
from urllib.parse import urlparse


from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import requests

import common

PAGES_DIR = Path("./pages")
PAGES_DIR.mkdir(exist_ok=True)

INVALID_PATH_CHARS_RE = re.compile(r'[\\/:\*\?"<>\| ]')


def normalize_title_for_path(title: str) -> str:
    title = INVALID_PATH_CHARS_RE.sub("_", title)
    return title


def title_from_link(page: str) -> str:
    return urlparse(page).path.rsplit("/", 1)[-1]


def get_soup(title: str) -> BeautifulSoup:
    title = title.replace(" ", "_")
    page = f"https://en.wikipedia.org/wiki/{title}"
    title = normalize_title_for_path(title)
    page_file = PAGES_DIR / (f"{title}.html")
    if page_file.exists():
        text = page_file.read_text(encoding="utf-8")
    else:
        res = requests.get(page)
        text = res.text
        page_file.write_text(text, encoding="utf-8")
    soup = BeautifulSoup(text, "lxml")
    return soup


## (( ))
def parens_are_matching(text: str) -> bool:
    open_stack = []
    close_stack = []
    for c in text:
        if c == "(":
            open_stack.append(c)
        elif c == ")":
            close_stack.append(c)
    while open_stack or close_stack:
        try:
            open_stack.pop()
            close_stack.pop()
        except:
            pass
    return not (open_stack or close_stack)


def link_is_parenthesized(element: Tag) -> bool:
    open_parens = False
    prev = element.previous_element
    while prev:
        if isinstance(prev, NavigableString):
            text = str(prev)
        else:
            text = ""
        open_idx = text.rfind("(")
        close_idx = text.rfind(")")
        if open_idx > close_idx:
            open_parens = True
            break
        elif close_idx != -1:
            break
        prev = prev.previous_element

    next_el = element.next_element
    while next_el:
        if isinstance(next_el, NavigableString):
            text = str(next_el)
        else:
            text = next_el.get_text()
        for c in text:
            if c == ")" and open_parens:
                return True
            elif c == "(" and not open_parens:
                return False
        next_el = next_el.next_element
    return False


def link_is_italicized(element: Tag) -> bool:
    parent = element.parent
    while parent and parent.name.lower() != "p":
        if parent.name.lower() == "i":
            return True
        parent = parent.parent
    return False


def should_crawl_link(element: Tag) -> bool:
    link = element["href"]
    title = title_from_link(link.replace("_", " "))
    ret = not common.is_namespace_title(title) and not link.endswith(
        "_(disambiguation)"
    )
    ret &= not link_is_parenthesized(element)
    ret &= not link_is_italicized(element)

    return ret


def _crawl(
    path: List[str],
    visited: Set[str],
    origin_title: str,
    target_title: str,
    limit: int,
    depth: int = 0,
) -> bool:
    print(f"crawling {origin_title}", file=sys.stderr)
    if origin_title == target_title:
        return True
    elif origin_title in visited:
        return False
    visited.add(origin_title)
    if depth + 1 > limit:
        return False
    soup = get_soup(origin_title)
    link_elements = soup.select('#mw-content-text p a[href^="/wiki/"]')
    wikilinks = (e for e in link_elements if should_crawl_link(e))

    for link in itertools.islice(wikilinks, 1):
        if _crawl(
            path,
            visited,
            title_from_link(link["href"]),
            target_title,
            limit,
            depth=depth + 1,
        ):
            path.append(title_from_link(link["href"]))
            return True
    return False


def go_to(origin_title: str, target_title: str, limit=1000) -> List[str]:
    path: List[str] = []
    visited: Set[str] = set()
    success = _crawl(path, visited, origin_title, target_title, limit)
    if success:
        path.append(origin_title)
    path.reverse()
    return path


def go_to_philosophy(origin_title: str, limit=1000) -> List[str]:
    return go_to(origin_title, "Philosophy", limit)


if __name__ == "__main__":
    titles = [
        # "Wikipedia:Getting_to_Philosophy",
        "Logic",
        # "Mathematics",
        # "Foobar",
        # "Philosophy",
        # "Dynamic_programming",
    ]
    for title in titles:
        path = go_to_philosophy(title)
        print(path)
