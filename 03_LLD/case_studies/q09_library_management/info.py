INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Library Management System.',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Library Management System LLD

The **Library Management System (LMS)** is a classic Low-Level Design problem that tests a candidate's ability to handle complex relationships between entities, state management (availability of books), and the application of SOLID principles to ensure the system is extensible.

---

## 1. Overview & System Requirements

The goal is to design a system that manages the operations of a physical library. The system must handle book inventories, member registrations, the borrowing process, and the return process.

### Core Actors
- **Librarian**: Responsible for adding/removing books, managing members, and processing loans.
- **Member**: A user who can search for books, reserve books, and borrow/return them.

### Functional Requirements
1. **Catalog Management**: Ability to search for books by title, author, or category.
2. **Inventory Management**: Distinguish between a **Book** (the conceptual work) and a **BookItem** (the physical copy with a unique barcode).
3. **Loan System**:
    - A member can borrow a book for a specific period.
    - A member has a limit on the number of books they can borrow simultaneously.
4. **Reservation System**: If all copies of a book are borrowed, a member can reserve it.
5. **Fine Management**: Calculate and collect fines for books returned past the due date.
6. **Account Management**: Maintain profiles for members and librarians.

---

## 2. Design Principles & Patterns

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: 
    - `Search` class handles only searching logic.
    - `BookLending` class handles only the loan lifecycle.
    - `FineService` handles only the calculation of penalties.
- **Open/Closed Principle (OCP)**: The system is open for extension (e.g., adding a new `Notification` method like SMS or Email) without modifying the core `BookLending` logic.
- **Liskov Substitution Principle (LSP)**: `Member` and `Librarian` inherit from a base `Account` class, ensuring they can be used interchangeably where account details are required.
- **Interface Segregation Principle (ISP)**: Instead of one massive "LibraryInterface," we split functionalities into `Searchable`, `Borrowable`, and `Manageable`.

### Design Patterns Used
| Pattern | Application | Why? |
| :--- | :--- | :--- |
| **Singleton** | `Library` Class | Ensures there is only one central registry of books and members throughout the application. |
| **Strategy** | `SearchStrategy` | Allows switching between searching by Title, Author, or ISBN without changing the client code. |
| **Factory** | `AccountFactory` | Decouples the creation of `Member` and `Librarian` objects from the main logic. |
| **Observer** | `ReservationSystem` | Notifies members automatically when a reserved book becomes available. |

---

## 3. Class Structure & Relationships

### Entity Relationship Logic
- **Book $\rightarrow$ BookItem**: One-to-Many. A "Clean Code" book has one entry in the catalog but five physical copies.
- **Member $\rightarrow$ BookLending**: One-to-Many. A member can have multiple active loans.
- **BookItem $\rightarrow$ BookLending**: One-to-One (Active). A specific physical copy can only be lent to one person at a time.

### ASCII Class Diagram
```text
+-------------------+          +-------------------+
|      Account      |<---------|    AccountFactory |
+-------------------+          +-------------------+
| - id: String      |
| - password: String|
+---------^---------+
          |
    +-----+-----+
    |           |
+---v-----+ +---v---------+
| Member  | | Librarian   |
+---------+ +-------------+
    |             |
    |             | (Manages)
    |             v
    |      +-------------------+
    |      |      Library      | <--- (Singleton)
    |      +-------------------+
    |      | - bookCatalog     |
    |      | - memberRegistry  |
    +----->| + issueBook()     |
           | + returnBook()    |
           +---------^---------+
                     |
           +---------+---------+
           |                   |
   +-------v-------+   +-------v-------+
   |    Search     |   |  BookLending  |
   +---------------+   +---------------+
   | + searchByT() |   | - creationDate|
   | + searchByA() |   | - dueDate     |
   +---------------+   | - returnDate  |
                       +---------------+
```

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation in Python

```python
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum

# --- Enums & Constants ---
class BookStatus(Enum):
    AVAILABLE = 1
    LOANED = 2
    RESERVED = 3
    LOST = 4

# --- Core Entities ---
class Book:
    def __init__(self, isbn, title, author, subject):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.subject = subject

class BookItem(Book):
    def __init__(self, isbn, title, author, subject, barcode):
        super().__init__(isbn, title, author, subject)
        self.barcode = barcode
        self.status = BookStatus.AVAILABLE
        self.dueDate = None

class Account(ABC):
    def __init__(self, id, password, name):
        self.id = id
        self.password = password
        self.name = name

class Member(Account):
    def __init__(self, id, password, name):
        super().__init__(id, password, name)
        self.total_books_checked_out = 0

class Librarian(Account):
    def __init__(self, id, password, name):
        super().__init__(id, password, name)

# --- Logic Components ---
class BookLending:
    def __init__(self, book_item, member):
        self.book_item = book_item
        self.member = member
        self.creation_date = datetime.now()
        self.due_date = self.creation_date + timedelta(days=14)
        self.return_date = None

    def mark_returned(self):
        self.return_date = datetime.now()

class Search:
    def __init__(self, library):
        self.library = library

    def search_by_title(self, title):
        return [book for book in self.library.books if book.title == title]

    def search_by_author(self, author):
        return [book for book in self.library.books if book.author == author]

# --- Main System (Singleton) ---
class Library:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Library, cls).__new__(cls)
            cls._instance.books = []
            cls._instance.members = {}
            cls._instance.active_lendings = {}
        return cls._instance

    def add_book(self, book_item):
        self.books.append(book_item)

    def issue_book(self, barcode, member_id):
        book_item = next((b for b in self.books if b.barcode == barcode), None)
        member = self.members.get(member_id)

        if book_item and member and book_item.status == BookStatus.AVAILABLE:
            if member.total_books_checked_out < 5:
                lending = BookLending(book_item, member)
                book_item.status = BookStatus.LOANED
                member.total_books_checked_out += 1
                self.active_lendings[barcode] = lending
                return f"Book {barcode} issued to {member.name}"
        return "Issue failed: Book unavailable or limit reached."

    def return_book(self, barcode):
        if barcode in self.active_lendings:
            lending = self.active_lendings.pop(barcode)
            lending.mark_returned()
            lending.book_item.status = BookStatus.AVAILABLE
            lending.member.total_books_checked_out -= 1
            
            # Fine calculation logic
            if lending.return_date > lending.due_date:
                overdue_days = (lending.return_date - lending.due_date).days
                return f"Book returned late. Fine: ${overdue_days * 1.5}"
            return "Book returned successfully."
        return "Invalid barcode."

# --- Execution ---
if __name__ == "__main__":
    lib = Library()
    # Setup
    b1 = BookItem("123", "Clean Code", "Robert Martin", "Tech", "BC001")
    lib.add_book(b1)
    
    m1 = Member("M1", "pass123", "Alice")
    lib.members["M1"] = m1
    
    search_engine = Search(lib)
    
    # Process
    print(lib.issue_book("BC001", "M1")) # Successful issue
    print(lib.return_book("BC001"))       # Successful return
```

### Logic Walkthrough
1. **Initialization**: The `Library` singleton is instantiated. `BookItems` are added to the catalog.
2. **Borrowing Flow**: 
   - The system verifies the `BookItem` exists and its status is `AVAILABLE`.
   - It checks if the `Member` has exceeded their loan limit (e.g., 5 books).
   - A `BookLending` record is created, the status is flipped to `LOANED`, and the `dueDate` is set to 14 days from today.
3. **Returning Flow**:
   - The system looks up the `BookLending` object using the barcode.
   - It calculates the difference between `return_date` and `due_date`.
   - If the difference is positive, a fine is calculated (e.g., \$1.50 per day).
   - The `BookItem` is marked `AVAILABLE` again.

---

## 5. Real-World Applications

The design patterns used in this Library Management System are applicable in several production-grade software environments:

1. **Digital Asset Management (DAM)**: Systems that manage licenses for software or digital assets (where "Book" is the Software Title and "BookItem" is the License Key).
2. **E-commerce Inventory**: Managing physical warehouse stock (SKUs vs. unique serialized items).
3. **Rental Services (Airbnb, Hertz)**: The "Loan" and "Return" logic is identical to renting a car or a room, including the logic for security deposits and late fees.
4. **Healthcare Systems**: Tracking medical equipment (ventilators, wheelchairs) that are "checked out" to specific patients or wards.

### Complexity Analysis
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Search by Title** | $O(N)$ | $O(1)$ | Linear scan through catalog. |
| **Issue Book** | $O(1)$ | $O(1)$ | Using HashMaps for lookup. |
| **Return Book** | $O(1)$ | $O(1)$ | Direct lookup via barcode. |
| **Space Usage** | $O(B + M)$ | - | $B = \text{Books}, M = \text{Members}$. |""",
    'solutions': """# System Design Document: Library Management System (LMS)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Catalog Management:**
    *   Librarians can add, update, and remove books, authors, and categories.
    *   The system must support multiple copies of the same book (Book vs. Book Item).
*   **Search & Discovery:**
    *   Members can search for books by title, author, subject, or publication date.
    *   Users can check the availability of a specific book copy.
*   **Member Management:**
    *   Users can register, update profiles, and view their borrowing history.
    *   Membership levels (e.g., Student, Faculty) may have different borrowing limits.
*   **Circulation (Borrowing & Returning):**
    *   Members can check out books (if they have no overdue fines and haven't reached their limit).
    *   Members can return books.
    *   The system automatically calculates due dates and overdue fines.
*   **Reservations:**
    *   Members can reserve a book that is currently checked out.
    *   The system notifies the member when the reserved book becomes available.
*   **Notifications:**
    *   Automatic reminders for upcoming due dates and overdue alerts.

### 1.2 Non-Functional Requirements
*   **Strong Consistency:** Ensuring a book cannot be borrowed by two people simultaneously (Race condition prevention).
*   **High Availability:** The search functionality should be available 24/7.
*   **Auditability:** Every loan and return must be logged for auditing.
*   **Extensibility:** Easy to add new rules (e.g., different fine structures for different book types).

### 1.3 Scale Estimations (Medium Scale)
*   **Users:** 100,000 registered members.
*   **Books:** 500,000 unique titles, 1 million physical copies.
*   **Traffic:** 10,000 Daily Active Users (DAU).
*   **Peak Load:** High traffic during university exam seasons or new releases.

---

## 2. High-Level Architecture

The system follows a **Layered Architecture** (Controller $\rightarrow$ Service $\rightarrow$ Repository).

### 2.1 Component Interaction
1.  **API Gateway:** Handles authentication, rate limiting, and request routing.
2.  **Search Service:** Utilizes an inverted index (like Elasticsearch) for fast full-text searching.
3.  **Circulation Service:** Manages the business logic for borrowing, returning, and reservations.
4.  **Member Service:** Manages user profiles and authentication.
5.  **Notification Service:** Asynchronous service that sends emails/SMS via a Message Queue.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    User((User/Librarian)) --> Gateway[API Gateway]
    Gateway --> MemberSvc[Member Service]
    Gateway --> SearchSvc[Search Service]
    Gateway --> CircSvc[Circulation Service]
    
    MemberSvc --> DB[(Primary SQL DB)]
    CircSvc --> DB
    
    SearchSvc --> ES[(Elasticsearch)]
    DB -.-> |CDC / Sync| ES
    
    CircSvc --> MQ[Message Queue]
    MQ --> NotifSvc[Notification Service]
    NotifSvc --> Email[Email/SMS Gateway]
```

---

## 3. Detailed Database Schema Design

### 3.1 Rationale for SQL
A Relational Database (PostgreSQL) is chosen because the system requires **ACID compliance**, particularly for the `Loans` and `BookItems` tables, to prevent double-booking and ensure financial accuracy for fines.

### 3.2 Schema Definition

#### `Books` (Core Metadata)
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `book_id` | UUID | PK | Unique identifier for the title |
| `isbn` | VARCHAR(13)| Unique, Indexed | International Standard Book Number |
| `title` | VARCHAR(255)| Indexed | Title of the book |
| `author_id` | UUID | FK $\rightarrow$ Authors | Reference to the author |
| `category_id` | UUID | FK $\rightarrow$ Categories| Reference to the category |
| `pub_date` | DATE | | Date of publication |

#### `BookItems` (Physical Copies)
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `barcode` | VARCHAR(50) | PK | Unique barcode on the physical book |
| `book_id` | UUID | FK $\rightarrow$ Books | Reference to the metadata |
| `status` | Enum | | AVAILABLE, LOANED, RESERVED, LOST |
| `rack_location`| VARCHAR(20) | | Physical location in the library |

#### `Members`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `member_id` | UUID | PK | Unique member ID |
| `name` | VARCHAR(100)| | Full name |
| `email` | VARCHAR(100)| Unique | User email |
| `member_type` | Enum | | STUDENT, FACULTY, STAFF |
| `joined_date` | DATE | | Registration date |

#### `Loans`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `loan_id` | UUID | PK | Unique loan ID |
| `barcode` | VARCHAR(50) | FK $\rightarrow$ BookItems| The specific copy borrowed |
| `member_id` | UUID | FK $\rightarrow$ Members | The member who borrowed it |
| `loan_date` | TIMESTAMP | | Date/Time of checkout |
| `due_date` | TIMESTAMP | | Expected return date |
| `return_date` | TIMESTAMP | Nullable | Actual return date |

#### `Reservations`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `res_id` | UUID | PK | Unique reservation ID |
| `book_id` | UUID | FK $\rightarrow$ Books | The title requested |
| `member_id` | UUID | FK $\rightarrow$ Members | Member waiting |
| `request_date` | TIMESTAMP | | When the hold was placed |
| `status` | Enum | | PENDING, COMPLETED, CANCELLED |

### 3.3 Indexing Strategy
*   **B-Tree Index** on `Books(title)` and `Books(isbn)` for fast lookup.
*   **Composite Index** on `Loans(member_id, return_date)` to quickly find active loans for a user.
*   **Index** on `BookItems(status)` to quickly filter available books.

---

## 4. Core API Design

### 4.1 Search Books
`GET /api/v1/books?title=...&author=...&category=...`
*   **Response:** `200 OK`
*   **Payload:**
    ```json
    [
      {
        "bookId": "uuid-123",
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "availableCopies": 2,
        "totalCopies": 5
      }
    ]
    ```

### 4.2 Checkout Book
`POST /api/v1/loans`
*   **Request:**
    ```json
    {
      "memberId": "uuid-member-1",
      "barcode": "BC-998877"
    }
    ```
*   **Response:** `201 Created` (or `400 Bad Request` if user has fines or book is unavailable).

### 4.3 Return Book
`POST /api/v1/loans/return`
*   **Request:**
    ```json
    {
      "barcode": "BC-998877"
    }
    ```
*   **Response:** `200 OK` with fine calculation details.

### 4.4 Reserve Book
`POST /api/v1/reservations`
*   **Request:**
    ```json
    {
      "memberId": "uuid-member-1",
      "bookId": "uuid-123"
    }
    ```
*   **Response:** `201 Created`.

---

## 5. Scalability & Advanced Topics

### 5.1 Concurrency Control
To prevent two users from borrowing the last copy of a book simultaneously:
*   **Optimistic Locking:** Use a `version` column in the `BookItems` table.
    *   `UPDATE BookItems SET status = 'LOANED', version = version + 1 WHERE barcode = '...' AND version = 5 AND status = 'AVAILABLE';`
*   If the update returns 0 rows, the system notifies the user that the book was just taken.

### 5.2 Search Optimization
*   **Elasticsearch:** Since SQL `LIKE %query%` is slow, sync the `Books` and `Authors` tables to Elasticsearch. Use a **Change Data Capture (CDC)** tool like Debezium to keep the search index updated in near real-time.

### 5.3 Caching Strategy
*   **Redis:** Cache frequently accessed book metadata and member session data.
*   **TTL:** Use a short TTL (e.g., 1 hour) for book availability since it changes frequently.

### 5.4 Async Notifications
*   Use a **Message Queue (RabbitMQ/Kafka)**. When a book is returned, the `Circulation Service` publishes a `BOOK_RETURNED` event. The `Notification Service` consumes this event and emails the first person in the `Reservations` queue.

---

## 6. Trade-off Analysis

### 6.1 Consistency vs. Availability (CAP Theorem)
In this system, **Consistency (C)** is prioritized over **Availability (A)** for circulation operations. It is unacceptable to allow two members to check out the same physical book. Therefore, we use a RDBMS with strong ACID guarantees for the loaning process.

### 6.2 Latency vs. Storage
We accept increased storage costs (by using Elasticsearch in addition to PostgreSQL) to achieve sub-second search latency. Indexing every title and author ensures that as the catalog grows to millions of books, the user experience remains fluid.

### 6.3 Normalization vs. Denormalization
The schema is highly normalized (3NF) to ensure data integrity (e.g., changing an author's name in one place updates all their books). However, for the Search API, we denormalize the data into a single Document in Elasticsearch to avoid expensive joins at query time.""",
}
