# Chatbot Platform HLD

A **Chatbot Platform** is a multi-tenant infrastructure that allows developers to build, deploy, and manage conversational agents. Unlike a single chatbot, a *platform* must handle diverse bot logic, multiple integration channels (Slack, WhatsApp, Web), state management for millions of concurrent users, and integration with Large Language Models (LLMs).

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Multi-Channel Integration**: Support for various front-ends (Web, Mobile, Slack, Discord, WhatsApp) via a unified adapter layer.
*   **Bot Management**: CRUD operations for bot configurations, prompt templates, and API keys.
*   **Message Routing**: Efficiently route user messages to the correct bot logic and return responses.
*   **Conversation State/Context**: Maintain session memory so bots "remember" previous turns in a conversation.
*   **LLM Integration**: Support for various LLM providers (OpenAI, Anthropic, Llama) and RAG (Retrieval-Augmented Generation) for private data.
*   **Asynchronous Processing**: Handle long-running LLM generations without blocking the connection.

### Non-Functional Requirements
*   **Low Latency**: User experience depends on "perceived real-time" responses. Target $< 200\text{ms}$ for routing, though LLM generation time is variable.
*   **High Availability**: The platform must be available $99.99\%$ of the time; a bot outage impacts business operations.
*   **Scalability**: Support millions of Daily Active Users (DAU) and thousands of unique bots.
*   **Durability**: Chat histories must be persisted for audit, training, and continuity.

### Scale Assumptions
| Metric | Value | Note |
| :--- | :--- | :--- |
| **Daily Active Users (DAU)** | $10\text{M}$ | Total users across all bots |
| **Avg Messages/User/Day** | $50$ | $500\text{M}$ messages per day |
| **Average QPS** | $\approx 5,800$ | $\text{Peak QPS} \approx 20,000+$ |
| **Storage per Message** | $500\text{ bytes}$ | Including metadata and context |
| **Daily Storage** | $\approx 250\text{ GB}$ | $\approx 90\text{ TB}$ per year |

---

## 2. High-Level System Architecture

The system follows a **microservices architecture** to decouple channel-specific logic from the core bot orchestration.

### Component Diagram Description
1.  **Channel Adapters**: Normalize incoming requests from different platforms (e.g., converting a Slack JSON payload to a standard Internal Message Format).
2.  **API Gateway**: Handles authentication, rate limiting, and request routing.
3.  **Chat Orchestrator**: The "brain" of the system. It fetches bot config, retrieves conversation context, and coordinates with the Bot Engine.
4.  **Context Store (Cache)**: A fast, distributed key-value store to hold the last $N$ messages of a conversation.
5.  **Bot Engine**: 
    *   **Internal Logic**: Executes predefined rules or scripts.
    *   **LLM Gateway**: Manages prompts, tokens, and calls to external LLM APIs.
    *   **RAG Pipeline**: Fetches relevant documents from a Vector Database to provide context to the LLM.
6.  **Message Queue (Kafka)**: Decouples the real-time response path from asynchronous tasks like analytics and long-term archival.
7.  **Persistence Layer**: 
    *   **NoSQL (Cassandra/DynamoDB)**: For chat history (write-heavy, partitioned by `conversation_id`).
    *   **Relational (PostgreSQL)**: For bot metadata, user accounts, and billing.
    *   **Vector DB (Pinecone/Milvus)**: For storing embeddings used in RAG.

---

## 3. Key HLD Concepts & Component Design

### A. The Context Window & State Management
Maintaining state is the hardest part of a chatbot platform.
*   **Session-based State**: Use **Redis** to store the most recent conversation turns. This avoids hitting the primary database for every message.
*   **Sliding Window**: Since LLMs have token limits, the orchestrator implements a sliding window, sending only the last $K$ messages or a summarized version of the history.
*   **TTL (Time to Live)**: Session data in Redis expires after $X$ hours of inactivity to save memory.

### B. LLM Gateway & Prompt Management
To avoid vendor lock-in and manage costs, an LLM Gateway is used:
*   **Prompt Templates**: Templates are stored in the DB. The Gateway injects user variables into these templates before sending them to the LLM.
*   **Token Counting**: Tracks usage per bot/user for billing and rate-limiting.
*   **Fallback Strategy**: If GPT-4 is down or hits a rate limit, the gateway can failover to Claude or a local Llama-3 instance.

### C. RAG (Retrieval-Augmented Generation) Pipeline
To make bots "knowledgeable" about specific company data:
1.  **Ingestion**: Documents $\rightarrow$ Chunking $\rightarrow$ Embedding Model $\rightarrow$ **Vector Database**.
2.  **Retrieval**: User Query $\rightarrow$ Embedding Model $\rightarrow$ Vector Similarity Search $\rightarrow$ Top-K Chunks.
3.  **Augmentation**: System Prompt + Top-K Chunks + User Query $\rightarrow$ LLM.

### D. Technology Stack Choices
| Component | Technology | Reason |
| :--- | :--- | :--- |
| **Database (History)** | Cassandra | Optimized for heavy writes; linear scalability via partitioning. |
| **Cache** | Redis | Sub-millisecond latency for session/context retrieval. |
| **Queue** | Kafka | High throughput for telemetry, logging, and async archival. |
| **Vector DB** | Pinecone/Milvus | Specialized for high-dimensional vector search (ANN). |
| **Communication** | WebSockets/gRPC | For real-time streaming of LLM tokens (typing effect). |

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Walkthrough (User $\rightarrow$ Bot)
1.  **Ingress**: User sends a message via WhatsApp.
2.  **Normalization**: The **WhatsApp Adapter** receives the webhook, validates the signature, and transforms it into a `StandardMessage` object.
3.  **Routing**: The **API Gateway** forwards the request to the **Chat Orchestrator**.
4.  **Context Retrieval**: The Orchestrator queries **Redis** using `conversation_id` to get the last 5 messages.
5.  **Knowledge Retrieval**: The Orchestrator calls the **RAG Pipeline** to fetch relevant document snippets from the **Vector DB**.
6.  **LLM Execution**: The **LLM Gateway** combines Context + RAG data + Prompt $\rightarrow$ calls OpenAI API $\rightarrow$ receives response.
7.  **Response Path**: The response is streamed back via the **Adapter** to WhatsApp.
8.  **Async Persistence**: The Orchestrator pushes the pair (User Message, Bot Response) to **Kafka**, which is then consumed by the **History Service** to be saved in **Cassandra**.

### Fault Tolerance & Reliability
*   **Dead Letter Queues (DLQ)**: If the History Service fails to write to Cassandra, Kafka moves the message to a DLQ for retry.
*   **Circuit Breakers**: If the LLM API latency spikes above $5\text{s}$, the circuit breaker trips, and the bot returns a "I'm experiencing heavy load, please try again later" message.
*   **Replication**: Cassandra uses a replication factor of 3 across different availability zones to ensure no data loss.
*   **Idempotency**: Every message is assigned a `client_msg_id` to prevent duplicate responses in case of network retries.

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
For a chatbot platform, **Availability (AP)** is prioritized over **Strong Consistency**. 
*   **Why?** If a user sends a message and the "read" receipt or history takes 1 second to sync across all nodes, it is acceptable. However, if the bot is unavailable for 1 second, the user perceives the system as broken.
*   **Consistency Model**: Eventual consistency for chat history.

### Latency vs. Quality (LLM Trade-off)
*   **The Dilemma**: Larger models (GPT-4) provide higher quality but higher latency and cost. Smaller models (GPT-3.5/Llama-3-8B) are faster.
*   **The Solution**: Implement **Model Routing**. Simple queries (e.g., "Hello", "What time is it?") are routed to a small model. Complex reasoning queries are routed to the large model.

### State Management: Local vs. Centralized
*   **Local (Sticky Sessions)**: Faster, but makes scaling/deployment difficult as users are tied to specific servers.
*   **Centralized (Redis)**: Slightly higher latency (network hop), but allows any application server to handle any request, enabling seamless horizontal scaling. **Chosen approach**.

---

## Summary Complexity Analysis

| Operation | Time Complexity | Space Complexity | Bottleneck |
| :--- | :--- | :--- | :--- |
| **Message Routing** | $O(1)$ | $O(1)$ | Network I/O |
| **Context Retrieval** | $O(1)$ (Redis) | $O(N)$ (Window size) | Memory |
| **RAG Vector Search**| $O(\log V)$ | $O(V \times D)$ | CPU/RAM for indexing |
| **LLM Generation** | $O(\text{Tokens})$ | $O(\text{Context Window})$ | GPU Compute/API Latency |