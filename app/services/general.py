from collections import deque
from urllib.parse import urljoin, urldefrag
from urllib.request import urlopen
from urllib.parse import urlsplit, urlunsplit, quote
from bs4 import BeautifulSoup
import re
import time

def getBaseUrl(url):
    match = re.match(r'http(s)?:\/\/.+\.(com|org|net|cd|uk|fr|app)', url)
    return str(match.group(0)) if match else None

def isInternalLink(link, base_url):
    return link in ["","#","/"] or link.startswith(("#","/")) or base_url == getBaseUrl(link)


def safe_url(url):
    parts = urlsplit(url)
    path = quote(parts.path)
    query = quote(parts.query, safe="=&?/")
    return urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def get_all_links_by_url(url, go_deep=False, timeout_per_request=30, max_pages:int |None=10000, max_depth:int |None=1000, max_runtime=None):
    internal_links = set()
    external_links = set()
    visited_pages = set()
    links_errors = set()
    base_url = getBaseUrl(url)

    queue = deque([(url, 0)])
    start = time.monotonic()
    max_depth_reached = 0
    error = None
    is_max_pages_not_exceeded = len(visited_pages) < max_pages
    if not is_max_pages_not_exceeded:
        error = f"max pages exceeded: ({max_pages})"

    while queue and is_max_pages_not_exceeded:
        if max_runtime is not None and (time.monotonic() - start) > max_runtime:
            error = f"max runtime exceeded: ({max_runtime}s)"
            break

        page_url, depth = queue.popleft()
        if depth > max_depth_reached:
            max_depth_reached = depth

        if page_url in visited_pages:
            continue
        visited_pages.add(page_url)

        try:
            html = urlopen(safe_url(page_url), timeout=timeout_per_request)
            bs = BeautifulSoup(html, "html.parser")
            all_links = bs.find_all("a")
            print(f"Found {len(all_links)} links in {page_url}")

            for link in all_links:
                href = link.attrs.get("href")
                if not href:
                    continue
                href = str(href)
                if href.startswith(("mailto:", "javascript:", "tel:", "data:")):
                    continue

                full_link = urljoin(page_url, href)
                full_link, _ = urldefrag(full_link)

                if isInternalLink(full_link, base_url):
                    if full_link not in internal_links:
                        internal_links.add(full_link)
                        if go_deep and depth + 1 <= max_depth:
                            queue.append((full_link, depth + 1))
                else:
                    external_links.add(full_link)

        except Exception as e:
            link_error = f"Error while getting {page_url} url: {repr(e)}"
            links_errors.add(link_error)
            print(link_error)

    elapsed = time.monotonic() - start
    return {
        "internal_links": internal_links,
        "external_links": external_links,
        "count_internal_links": len(internal_links),
        "count_external_links": len(external_links),
        "count_total_links": len(internal_links) + len(external_links),
        "max_depth_reached": max_depth_reached,
        "elapsed_seconds": elapsed,
        "links_errors": links_errors,
        "error": error,
    }