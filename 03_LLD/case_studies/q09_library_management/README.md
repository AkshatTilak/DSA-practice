# Library Management System LLD

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
| **Space Usage** | $O(B + M)$ | - | $B = \text{Books}, M = \text{Members}$. |