INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design URL Shortener (bit.ly) - LLD focus.',
    'groups': ['OOP Case Studies', 'Hashing'],
    'readme_content': """# URL Shortener LLD

A URL Shortener (like bit.ly or tinyurl.com) is a classic Low-Level Design problem that tests a developer's ability to handle **data encoding**, **mapping**, and **extensibility**. The goal is to map a long, cumbersome URL to a short, unique alphanumeric string and redirect users back to the original destination when the short string is accessed.

---

## 1. Overview & System Requirements

### Core Entities
- **Long URL**: The original destination address.
- **Short URL (Alias)**: The generated unique identifier (e.g., `bit.ly/3xKz2L`).
- **URL Mapping**: The association between the short code and the long URL.

### Functional Requirements
- **Shorten URL**: Convert a long URL into a short, unique alphanumeric code.
- **Expand URL**: Retrieve the original long URL given a short code and redirect the user.
- **Custom Alias**: Allow users to provide their own short code (if not already taken).
- **Expiration**: (Optional but recommended) Support a Time-to-Live (TTL) for shortened links.

### Non-Functional Requirements
- **Uniqueness**: No two long URLs should result in the same short code (unless intentionally designed for deduplication).
- **Efficiency**: Shortening and expansion should occur in constant time $O(1)$.
- **Scalability**: The design should allow switching from in-memory storage to a database without changing business logic.

---

## 2. Design Principles & Patterns

### Design Principles (SOLID)
- **Single Responsibility Principle (SRP)**: The `EncodingStrategy` handles the math of shortening, the `Storage` handles persistence, and the `URLShortenerService` orchestrates the process.
- **Open/Closed Principle (OCP)**: By using an interface for the encoding strategy, we can introduce new algorithms (e.g., Hash-based vs. Counter-based) without modifying the service class.
- **Dependency Inversion Principle (DIP)**: The high-level `URLShortenerService` depends on abstractions (`IStorage`, `IEncodingStrategy`) rather than concrete implementations.

### Design Patterns Applied
1. **Strategy Pattern**: Used for the encoding logic. Since there are multiple ways to generate a short code (Base62, MD5 hashing, etc.), the Strategy pattern allows the system to switch algorithms at runtime.
2. **Singleton Pattern**: The `URLShortenerService` is typically implemented as a singleton to maintain a consistent state of the counter and storage across the application.
3. **Factory Pattern**: (Optional) Can be used to instantiate different storage types (e.g., `RedisStorage` vs. `SQLStorage`).

---

## 3. Class Structure & Relationships

### Class Diagram (Text-Based)
```mermaid
classDiagram
    class URLShortenerService {
        - IStorage storage
        - IEncodingStrategy encoder
        + shortenURL(longUrl, customAlias) : String
        + expandURL(shortCode) : String
    }
    
    class IEncodingStrategy {
        <<interface>>
        + encode(id : long) : String
        + decode(shortCode : String) : long
    }
    
    class Base62Encoder {
        - charset : String
        + encode(id) : String
        + decode(shortCode) : long
    }
    
    class IStorage {
        <<interface>>
        + save(shortCode, longUrl) : void
        + get(shortCode) : String
        + exists(shortCode) : boolean
    }
    
    class InMemoryStorage {
        - map : Map<String, String>
        + save(shortCode, longUrl) : void
        + get(shortCode) : String
        + exists(shortCode) : boolean
    }

    URLShortenerService --> IStorage
    URLShortenerService --> IEncodingStrategy
    IEncodingStrategy <|.. Base62Encoder
    IStorage <|.. InMemoryStorage
```

### Relationships
- **Composition**: `URLShortenerService` *has-a* `IStorage` and *has-a* `IEncodingStrategy`.
- **Realization**: `Base62Encoder` implements `IEncodingStrategy`; `InMemoryStorage` implements `IStorage`.

---

## 4. Step-by-Step Logic & Code Walkthrough

### The Logic: Base62 Encoding
Instead of hashing (which can have collisions), the most robust LLD approach uses a **Global Unique ID (Counter)**.
1. Every long URL is assigned a unique numeric ID (1, 2, 3...).
2. This ID is converted from Base10 (decimal) to **Base62** (characters `[a-z, A-Z, 0-9]`).
3. A Base62 string of length 7 can support $62^7 \approx 3.5$ trillion unique URLs.

### Implementation

```python
import threading

# --- Strategy Pattern for Encoding ---
class IEncodingStrategy:
    def encode(self, numeric_id: int) -> str:
        pass

class Base62Encoder(IEncodingStrategy):
    def __init__(self):
        self.charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def encode(self, numeric_id: int) -> str:
        if numeric_id == 0:
            return self.charset[0]
        
        arr = []
        while numeric_id:
            arr.append(self.charset[numeric_id % 62])
            numeric_id //= 62
        return "".join(reversed(arr))

# --- Storage Interface ---
class IStorage:
    def save(self, short_code: str, long_url: str):
        pass
    def get(self, short_code: str) -> str:
        pass
    def exists(self, short_code: str) -> bool:
        pass

class InMemoryStorage(IStorage):
    def __init__(self):
        self._store = {}

    def save(self, short_code: str, long_url: str):
        self._store[short_code] = long_url

    def get(self, short_code: str) -> str:
        return self._store.get(short_code)

    def exists(self, short_code: str) -> bool:
        return short_code in self._store

# --- Main Service ---
class URLShortenerService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(URLShortenerService, cls).__new__(cls)
        return cls._instance

    def __init__(self, storage: IStorage, encoder: IEncodingStrategy):
        # Prevent re-initialization in Singleton
        if hasattr(self, 'initialized'): return
        self.storage = storage
        self.encoder = encoder
        self.counter = 1000000000  # Start from a high number for consistent length
        self.counter_lock = threading.Lock()
        self.initialized = True

    def shorten_url(self, long_url: str, custom_alias: str = None) -> str:
        if custom_alias:
            if self.storage.exists(custom_alias):
                raise ValueError("Custom alias already exists!")
            self.storage.save(custom_alias, long_url)
            return custom_alias

        with self.counter_lock:
            short_code = self.encoder.encode(self.counter)
            self.counter += 1
        
        self.storage.save(short_code, long_url)
        return short_code

    def expand_url(self, short_code: str) -> str:
        url = self.storage.get(short_code)
        if not url:
            raise ValueError("Short URL not found!")
        return url

# --- Execution ---
if __name__ == "__main__":
    storage = InMemoryStorage()
    encoder = Base62Encoder()
    service = URLShortenerService(storage, encoder)

    # Case 1: Standard Shortening
    url1 = "https://www.google.com/search?q=low+level+design+patterns"
    code1 = service.shorten_url(url1)
    print(f"Long: {url1} -> Short: {code1}")
    print(f"Expand: {service.expand_url(code1)}")

    # Case 2: Custom Alias
    url2 = "https://github.com/openai"
    code2 = service.shorten_url(url2, custom_alias="openai-git")
    print(f"Long: {url2} -> Short: {code2}")
    print(f"Expand: {service.expand_url(code2)}")
```

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Shorten URL** | $O(1)$ | $O(1)$ | Base62 encoding takes $\log_{62}(N)$ time, which is constant for a fixed max ID. |
| **Expand URL** | $O(1)$ | $O(1)$ | Hash map lookup is constant time. |
| **Storage** | N/A | $O(N)$ | Space grows linearly with the number of URLs stored. |

---

## 6. Real-World Applications

1. **Bitly / TinyURL**: These services use the exact Base62 encoding and distributed ID generation (e.g., Snowflake IDs) to ensure uniqueness across multiple servers.
2. **Marketing Campaigns**: Using custom aliases (e.g., `brand.ly/summer-sale`) for tracking and branding.
3. **API Gateways**: Shortening complex internal resource paths to provide cleaner external endpoints.
4. **Social Media**: Platforms like Twitter (X) automatically shorten long links to save character space and track click-through rates (CTR).

### Production Considerations (Beyond LLD)
- **Distributed ID Generation**: In a real distributed system, a single `counter` variable is a bottleneck. Engineers use **Zookeeper** or **Twitter Snowflake** to generate unique IDs across multiple nodes.
- **Caching**: Use **Redis** to cache the most frequently accessed `shortCode -> longUrl` mappings to reduce database load.
- **Database**: Use a **NoSQL Key-Value store** (like DynamoDB or Cassandra) because the access pattern is a simple key-value lookup.""",
    'solutions': """# System Design Document: URL Shortener (bit.ly)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **URL Shortening:** The system should take a long URL and return a shorter, unique alias.
*   **URL Redirection:** When a user accesses the short URL, the system should redirect them to the original long URL with minimum latency.
*   **Custom Aliases:** Users should be able to provide a custom string for their short URL.
*   **Expiration:** URLs should have a default or user-defined expiration date.
*   **Analytics:** The system should track the number of clicks and basic metadata (timestamp, location) for each short URL.

### 1.2 Non-Functional Requirements
*   **High Availability:** The redirection service must be available 24/7; downtime results in broken links across the web.
*   **Low Latency:** Redirection should happen in milliseconds.
*   **Uniqueness:** No two different long URLs should result in the same short URL (unless explicitly intended).
*   **Scalability:** The system must handle a high volume of read requests (redirections) compared to write requests (shortening).

### 1.3 Scale Estimations
*   **Write Volume:** Assume 100 million URLs created per month.
*   **Read Volume:** Assume a 10:1 read-to-write ratio $\rightarrow$ 1 billion redirections per month.
*   **Storage:** If each record is $\sim 500$ bytes, 100M records/month $\times 12$ months $\times 5$ years $\approx 3$ TB of data.
*   **TPS (Transactions Per Second):** 
    *   Write: $100M / (30 \times 24 \times 3600) \approx 38$ writes/sec.
    *   Read: $1B / (30 \times 24 \times 3600) \approx 385$ reads/sec.
    *   *Note: Peak loads can be $10\times$ higher.*

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **API Gateway/Load Balancer:** Distributes incoming traffic across multiple application servers.
2.  **Shortening Service:** Handles the logic of generating unique short keys and storing the mapping.
3.  **Redirection Service:** High-performance service that resolves short keys to long URLs and handles HTTP redirects.
4.  **Key Generation Service (KGS):** A dedicated service to provide unique IDs to avoid collisions in a distributed environment.
5.  **Cache (Redis):** Stores frequently accessed URL mappings to reduce database load.
6.  **Database:** Persistent storage for URL mappings and user data.

### 2.2 Architecture Diagram
```mermaid
graph TD
    User((User)) --> LB[Load Balancer]
    LB --> AppSrv[Application Servers]
    
    subgraph "Application Logic"
        AppSrv --> ShortSrv[Shortening Service]
        AppSrv --> RedirSrv[Redirection Service]
    end
    
    ShortSrv --> KGS[Key Generation Service]
    ShortSrv --> DB[(Database)]
    RedirSrv --> Cache[(Redis Cache)]
    Cache --> DB
    
    RedirSrv --> Analytics[Analytics Queue/Worker]
    Analytics --> StatsDB[(Stats DB/ClickHouse)]
```

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection
Since the data model is a simple Key-Value pair (ShortURL $\rightarrow$ LongURL) and we require massive scalability and high availability, a **NoSQL Database (like Cassandra or DynamoDB)** is preferred. 
*   **Reasoning:** NoSQL scales horizontally more easily than SQL. We do not need complex joins. The primary access pattern is a point lookup by the short key.

### 3.2 Schema Definition

#### Table: `url_mapping`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `short_key` | `VARCHAR(10)` | **PK** | The unique Base62 encoded string. |
| `original_url` | `TEXT` | Not Null | The destination long URL. |
| `user_id` | `UUID` | Indexed | Owner of the URL for management. |
| `created_at` | `TIMESTAMP` | Not Null | Creation timestamp. |
| `expires_at` | `TIMESTAMP` | Indexed | Expiration date. |

#### Table: `url_analytics`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `short_key` | `VARCHAR(10)` | **PK/Partition** | Foreign key to `url_mapping`. |
| `timestamp` | `TIMESTAMP` | **Sort Key** | When the click occurred. |
| `ip_address` | `VARCHAR(45)` | - | User's IP. |
| `user_agent` | `TEXT` | - | Browser/OS info. |
| `referrer` | `TEXT` | - | Where the user came from. |

### 3.3 Indexing Strategy
*   **Primary Key:** `short_key` ensures $O(1)$ lookup.
*   **Secondary Index:** `user_id` allows users to list all URLs they have shortened.
*   **TTL Index:** In MongoDB or DynamoDB, a TTL index on `expires_at` can automatically purge expired records.

---

## 4. Core API Design

### 4.1 Shorten URL
`POST /api/v1/shorten`

**Request Body:**
```json
{
  "longUrl": "https://www.example.com/some/very/long/path/to/article?id=123",
  "customAlias": "my-promo-2024", 
  "expiryDate": "2025-12-31T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
  "shortUrl": "https://bit.ly/my-promo-2024",
  "createdAt": "2024-01-01T10:00:00Z"
}
```

### 4.2 Redirect URL
`GET /{shortKey}`

**Response:** 
*   **302 Found (Temporary Redirect):** Used so that every click is tracked by our servers (doesn't get cached by the browser permanently).
*   **Header:** `Location: https://www.example.com/some/very/long/path...`

### 4.3 Get Analytics
`GET /api/v1/stats/{shortKey}`

**Response (200 OK):**
```json
{
  "shortKey": "my-promo-2024",
  "totalClicks": 1540,
  "topReferrers": [
    {"source": "twitter.com", "count": 800},
    {"source": "facebook.com", "count": 740}
  ]
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Key Generation Logic (The Core Challenge)
To avoid collisions in a distributed system, we use **Base62 Encoding** ($[0-9, a-z, A-Z]$). 
A 7-character string gives $62^7 \approx 3.5$ trillion combinations.

**The Approach: Distributed ID Generation (KGS)**
1.  We use a distributed counter (e.g., via **Apache ZooKeeper**).
2.  The KGS maintains a range of IDs (e.g., Server A gets 1-1000, Server B gets 1001-2000).
3.  When a request comes, the application server takes the next available integer ID and converts it to Base62.
4.  This eliminates the need for "check-then-insert" database calls, preventing race conditions.

### 5.2 Caching Strategy
Since the read-to-write ratio is high, a caching layer is mandatory.
*   **Technology:** Redis.
*   **Eviction Policy:** LRU (Least Recently Used).
*   **Flow:** `RedirSrv` $\rightarrow$ `Redis` $\rightarrow$ (if miss) $\rightarrow$ `DB` $\rightarrow$ `Populate Redis`.

### 5.3 Data Sharding
To handle growth, we shard the database based on the hash of the `short_key`.
*   **Consistent Hashing:** Ensures that adding/removing database nodes doesn't result in massive data migration.

### 5.4 Rate Limiting
To prevent API abuse (spamming the shorten endpoint), we implement a Rate Limiter (Token Bucket algorithm) at the API Gateway, keyed by `user_id` or `IP address`.

### 5.5 Asynchronous Analytics
Writing analytics data to the database on every redirect would bottleneck the `Redirection Service`.
*   **Pipeline:** `RedirSrv` $\rightarrow$ `Kafka/RabbitMQ` $\rightarrow$ `Analytics Consumer` $\rightarrow$ `ClickHouse/Cassandra`.
*   This decouples the critical path (redirecting the user) from the non-critical path (logging the click).

---

## 6. Trade-off Analysis

| Trade-off | Selection | Justification |
| :--- | :--- | :--- |
| **Redirect Type** | `302 Found` vs `301 Moved Permanently` | **302** is chosen. 301 is cached by browsers, meaning we lose analytics for subsequent visits. 302 ensures every request hits our server. |
| **CAP Theorem** | Availability over Consistency (AP) | In a global system, the user's ability to be redirected is more important than seeing the "exact" click count in real-time. |
| **ID Generation** | KGS vs Hashing (MD5/SHA) | **KGS** is chosen. Hashing long URLs requires collision handling (appending salts and re-hashing), which increases latency and DB load. |
| **Storage** | NoSQL vs SQL | **NoSQL** is chosen for horizontal scalability and the simplicity of the key-value access pattern. |
| **Latency vs Storage** | Memory Cache vs DB | We prioritize **Latency**. We use significant RAM (Redis) to ensure that the "hot" 20% of URLs (which drive 80% of traffic) are resolved in $<10\text{ms}$. |""",
}
