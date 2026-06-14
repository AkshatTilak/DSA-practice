# Web Crawler LLD

A **Web Crawler** (or spider) is a system that systematically browses the World Wide Web, typically for the purpose of indexing pages for a search engine. Designing an **extensible** web crawler requires a careful balance between concurrency, politeness (respecting server limits), and the ability to handle diverse content types and storage backends.

---

## 1. Overview & System Requirements

### Core Objective
Build a system that starts with a set of "seed" URLs, fetches the content of those pages, extracts all outgoing links, and recursively visits those links while ensuring no page is visited twice and the target servers are not overwhelmed.

### Functional Requirements
- **URL Frontier**: Manage a queue of URLs to be visited.
- **Duplicate Detection**: Ensure the same URL is not processed multiple times.
- **Fetching**: Retrieve the HTML content of a page.
- **Parsing**: Extract links and specific data from the retrieved content.
- **Robots.txt Compliance**: Respect the crawling rules defined by the website owner.
- **Extensibility**: Support different parsing strategies (HTML, PDF, JSON) and different storage backends.

### Non-Functional Requirements
- **Scalability**: Handle millions of pages through concurrency.
- **Politeness**: Implement delays between requests to the same domain.
- **Robustness**: Handle timeouts, 404s, and malformed HTML.

---

## 2. Design Principles & Patterns

To ensure the design is "extensible," we apply several software engineering patterns:

### A. Strategy Pattern
**Application**: Used for `ParsingStrategy` and `CrawlingStrategy`.
**Why**: Different websites require different parsing logic (e.g., an HTML parser vs. a PDF parser). By encapsulating these in strategies, we can add new file-type support without modifying the core `CrawlerEngine`.

### B. Factory Pattern
**Application**: `ParserFactory` and `FetcherFactory`.
**Why**: The system should decide at runtime which parser to use based on the `Content-Type` header of the HTTP response. The Factory decouples the selection logic from the execution logic.

### C. Singleton Pattern
**Application**: `ConfigurationManager` or `DatabaseConnection`.
**Why**: Ensures that system-wide settings (like max threads or timeout limits) are consistent across all worker threads.

### D. SOLID Principles
- **Single Responsibility (SRP)**: The `Fetcher` only downloads; the `Parser` only extracts; the `UrlFrontier` only manages the queue.
- **Open/Closed Principle**: The system is open for extension (adding new `IParser` implementations) but closed for modification of the `CrawlerEngine`.
- **Dependency Inversion (DIP)**: The `CrawlerEngine` depends on interfaces (`IParser`, `IFetcher`) rather than concrete classes.

---

## 3. Class Structure & Relationships

### Class Diagram (Conceptual)

```text
+-------------------+          +-------------------+
|   CrawlerEngine   | -------->|    UrlFrontier    |
+-------------------+          +-------------------+
          |                             |
          | (uses)                      | (manages)
          v                             v
+-------------------+          +-------------------+
|    IFetcher       |          |      URL          |
+-------------------+          +-------------------+
          ^                             ^
          |                             |
+-------------------+          +-------------------+
|   HttpFetcher     |          |   VisitedSet      |
+-------------------+          +-------------------+
          |
          v
+-------------------+          +-------------------+
|    IParser        | <--------|   ParserFactory   |
+-------------------+          +-------------------+
          ^                             |
          |                             |
    +-----+-----+                       |
    |           |                       |
+-----------+ +-----------+             |
| HtmlParser| | PdfParser | <-----------+
+-----------+ +-----------+
```

### Component Definitions

| Component | Responsibility | Key Methods |
| :--- | :--- | :--- |
| **UrlFrontier** | Manages the queue of pending URLs and tracks visited ones. | `add_url()`, `get_next_url()` |
| **IFetcher** | Interface for downloading content. | `fetch(url)` |
| **IParser** | Interface for extracting links/data. | `parse(content)` |
| **ParserFactory** | Returns the appropriate parser based on content type. | `get_parser(content_type)` |
| **CrawlerEngine** | The orchestrator that ties all components together. | `start_crawling()` |

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Thread, Lock
import requests
from bs4 import BeautifulSoup
import time

# --- Interfaces ---

class IParser(ABC):
    @abstractmethod
    def parse(self, content: str):
        pass

class IFetcher(ABC):
    @abstractmethod
    def fetch(self, url: str) -> tuple:
        pass

# --- Concrete Implementations ---

class HtmlParser(IParser):
    def parse(self, content: str):
        soup = BeautifulSoup(content, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        return links

class PdfParser(IParser):
    def parse(self, content: str):
        print("Parsing PDF content...")
        return [] # Simplified for LLD

class HttpFetcher(IFetcher):
    def fetch(self, url: str):
        try:
            response = requests.get(url, timeout=5)
            return response.text, response.headers.get('Content-Type', 'text/html')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None, None

class ParserFactory:
    @staticmethod
    def get_parser(content_type: str) -> IParser:
        if 'text/html' in content_type:
            return HtmlParser()
        elif 'application/pdf' in content_type:
            return PdfParser()
        return None

# --- Core System ---

class UrlFrontier:
    def __init__(self):
        self.queue = Queue()
        self.visited = set()
        self.lock = Lock()

    def add_url(self, url: str):
        with self.lock:
            if url not in self.visited:
                self.visited.add(url)
                self.queue.put(url)

    def get_next_url(self):
        try:
            return self.queue.get(timeout=2)
        except Empty:
            return None

class CrawlerEngine:
    def __init__(self, fetcher: IFetcher, frontier: UrlFrontier, num_threads: int = 4):
        self.fetcher = fetcher
        self.frontier = frontier
        self.num_threads = num_threads

    def _worker(self):
        while True:
            url = self.frontier.get_next_url()
            if url is None: break
            
            print(f"Crawling: {url}")
            content, content_type = self.fetcher.fetch(url)
            
            if content:
                parser = ParserFactory.get_parser(content_type)
                if parser:
                    links = parser.parse(content)
                    for link in links:
                        # In a real scenario, we'd normalize the URL here
                        if link.startswith('http'):
                            self.frontier.add_url(link)
            
            time.sleep(1) # Politeness delay

    def start(self, seeds):
        for seed in seeds:
            self.frontier.add_url(seed)
        
        threads = []
        for _ in range(self.num_threads):
            t = Thread(target=self._worker)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

# --- Execution ---
if __name__ == "__main__":
    frontier = UrlFrontier()
    fetcher = HttpFetcher()
    engine = CrawlerEngine(fetcher, frontier, num_threads=2)
    
    # Start with a seed URL
    engine.start(["https://example.com"])
```

### Logic Walkthrough
1.  **Initialization**: The `CrawlerEngine` is initialized with a `Fetcher` and a `UrlFrontier`. This allows us to swap `HttpFetcher` for a `MockFetcher` during testing (Dependency Injection).
2.  **Seeding**: Seed URLs are added to the `UrlFrontier`. The `visited` set prevents the crawler from entering infinite loops.
3.  **Concurrency**: Multiple worker threads are spawned. Each thread polls the `UrlFrontier` for a new URL.
4.  **Fetching & Factory**: The `HttpFetcher` retrieves the page. The `ParserFactory` inspects the `Content-Type` header to decide whether an `HtmlParser` or `PdfParser` should handle the data.
5.  **Expansion**: The `IParser` extracts new links, which are fed back into the `UrlFrontier`, expanding the crawl horizon.
6.  **Politeness**: A `time.sleep(1)` is implemented to avoid slamming a single server with requests.

---

## 5. Complexity & Performance Analysis

### Time and Space Complexity

| Metric | Complexity | Description |
| :--- | :--- | :--- |
| **Time Complexity** | $O(V + E)$ | Where $V$ is the number of unique pages (vertices) and $E$ is the number of links (edges). |
| **Space Complexity** | $O(V)$ | The `visited` set must store every unique URL encountered to prevent duplicates. |
| **Concurrency** | $O(T)$ | Throughput increases linearly with the number of threads $T$, until I/O or CPU saturation occurs. |

### Real-World Production Applications
1.  **Search Engines (Google/Bing)**: Use massively distributed crawlers. Instead of a local `Queue`, they use distributed messaging systems like **Apache Kafka**.
2.  **Price Aggregators**: Use specialized `Parsers` for different e-commerce sites (Amazon, eBay) to extract pricing data into a structured database.
3.  **SEO Audit Tools**: Use crawlers to find broken links (404s) and analyze metadata across thousands of pages of a corporate site.
4.  **Web Archiving (Wayback Machine)**: Focuses on high-fidelity `Fetchers` that save the entire state of a page, including CSS and JS assets.