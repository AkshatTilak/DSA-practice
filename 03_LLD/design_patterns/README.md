# Thread-Safe Singleton Pattern

The Singleton is a creational design pattern that restricts instantiation of a class to a single object instance. In multithreaded applications, securing thread-safety via lock guards and double-checked locking ensures that concurrent threads do not accidentally instantiate multiple instances.

---

## 🗺️ ASCII Execution Flow: Double-Checked Locking

Double-Checked Locking optimizes performance by checking if the instance is initialized *before* acquiring a thread lock, and checking *again* after acquiring it:

```text
Thread Call ──> Check 1: Is instance created?
                     │
                     ├─ Yes ──> Return instance (No lock overhead)
                     │
                     └─ No  ──> Acquire Thread Lock
                                     │
                                     └── Check 2: Is instance created *still* null?
                                              │
                                              ├─ Yes ──> Instantiate object
                                              │          Release Lock
                                              │          Return instance
                                              │
                                              └─ No  ──> Release Lock (Another thread initialized it)
                                                         Return instance
```

---

## 🏢 Real-World Production Use-Case

### Amazon: DynamoDB Local Client Connection Pool
In serverless applications (e.g. AWS Lambda functions), maintaining network connections to databases can be expensive.
1. When a Lambda function container spins up to handle requests, it initializes a DynamoDB client instance.
2. The client is implemented as a thread-safe **Singleton** database pool manager.
3. Every incoming thread/request reuse this single connection pool manager. This avoids high latency connection handshake overheads and prevents the database from being overwhelmed with thousands of idle network connections.
