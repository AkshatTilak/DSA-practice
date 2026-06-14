INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Chatbot Platform.',
    'groups': ['Real-World Systems'],
    'readme_content': """# Chatbot Platform HLD

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
| **LLM Generation** | $O(\text{Tokens})$ | $O(\text{Context Window})$ | GPU Compute/API Latency |""",
    'solutions': """# System Design Document: Enterprise Chatbot Platform

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Bot Management:** Businesses should be able to create, configure, and version multiple chatbots.
*   **Multi-Channel Integration:** Support for various front-ends (Web Widget, WhatsApp, Slack, Facebook Messenger).
*   **Conversation Orchestration:** 
    *   **Intent-based:** Rule-based flows or intent matching.
    *   **LLM-based:** Integration with Large Language Models (OpenAI, Claude, etc.) for generative responses.
    *   **RAG (Retrieval Augmented Generation):** Ability to upload knowledge bases (PDFs, Docs) for the bot to reference.
*   **Session Management:** Maintain state/context across a conversation.
*   **Human Handoff:** Ability to transfer the conversation to a live human agent.
*   **Analytics:** Track user engagement, drop-off rates, and intent accuracy.

### 1.2 Non-Functional Requirements
*   **Low Latency:** Responses should feel real-time (< 2 seconds for rule-based, streaming for LLM).
*   **High Availability:** The platform must be available 24/7; bot downtime equals business loss.
*   **Scalability:** Handle millions of concurrent users across thousands of different bots.
*   **Extensibility:** Easy to add new LLM providers or messaging channels without rewriting the core engine.
*   **Isolation:** One bot's heavy load or configuration error should not affect other bots.

### 1.3 Scale Estimations (HLD)
*   **Daily Active Users (DAU):** 10 million users across all bots.
*   **Average Messages per User/Day:** 10 messages.
*   **Total Daily Volume:** 100 million messages.
*   **Average QPS:** $\approx 1,150$ requests per second.
*   **Peak QPS:** $\approx 10,000$ requests per second.
*   **Storage:** Chat history for 100M messages/day $\approx$ 5-10 TB per month (assuming 50-100 bytes per message including metadata).

---

## 2. High-Level Architecture

The system follows a microservices architecture to decouple channel-specific logic from the core conversation engine.

### 2.1 Component Diagram

```mermaid
graph TD
    User((User)) --> Channel[Channel Gateway: Web/WhatsApp/Slack]
    Channel --> API_Gateway[API Gateway / Load Balancer]
    
    API_Gateway --> Bot_Mgmt[Bot Management Service]
    API_Gateway --> Conv_Engine[Conversation Engine]
    
    Bot_Mgmt --> Config_DB[(Bot Config DB - PostgreSQL)]
    
    Conv_Engine --> Session_Store[(Session Cache - Redis)]
    Conv_Engine --> History_DB[(Chat History - Cassandra/DynamoDB)]
    
    Conv_Engine --> Orchestrator{Orchestrator}
    Orchestrator --> Intent_Engine[Intent/Rule Engine]
    Orchestrator --> LLM_Gateway[LLM Gateway]
    
    LLM_Gateway --> Vector_DB[(Vector DB - Pinecone/Milvus)]
    LLM_Gateway --> External_LLM[External LLMs: OpenAI/Anthropic]
    
    Conv_Engine --> Event_Bus[Message Queue - Kafka]
    Event_Bus --> Analytics_Svc[Analytics Service]
    Event_Bus --> Human_Handoff[Handoff Service]
```

### 2.2 Core Component Interactions
1.  **Channel Gateway:** Normalizes incoming payloads from different providers (e.g., converting a WhatsApp JSON to a standard internal `Message` object).
2.  **Conversation Engine:** The central brain. It fetches the current session state, identifies the bot configuration, and determines the next action.
3.  **Orchestrator:** Decides whether the request should be handled by a predefined rule (Intent Engine) or passed to a generative model (LLM Gateway).
4.  **LLM Gateway:** Manages prompt templates, handles RAG by querying the Vector DB for relevant context, and manages API keys/rate limits for external LLM providers.
5.  **Session Store:** Stores short-term memory (e.g., "The user is currently in the 'Checkout' flow").

---

## 3. Detailed Database Schema Design

### 3.1 Relational Database (PostgreSQL)
Used for structured data requiring ACID compliance: Bot configurations, user accounts, and billing.

**Table: `bots`**
| Field | Type | Description |
| :--- | :--- | :--- |
| `bot_id` | UUID (PK) | Unique identifier for the bot |
| `owner_id` | UUID (FK) | Link to the business account |
| `name` | VARCHAR | Display name |
| `config_json` | JSONB | General settings (greeting, timeout, etc.) |
| `version` | INT | Current active version of the bot logic |
| `created_at` | TIMESTAMP | Audit trail |

**Table: `bot_flows`** (For rule-based bots)
| Field | Type | Description |
| :--- | :--- | :--- |
| `flow_id` | UUID (PK) | Unique flow ID |
| `bot_id` | UUID (FK) | Associated bot |
| `state_name` | VARCHAR | Name of the state (e.g., "ASK_EMAIL") |
| `response_text`| TEXT | What the bot says |
| `next_state` | VARCHAR | Transition logic |

### 3.2 NoSQL Database (Cassandra / DynamoDB)
Used for chat history due to high write volume and time-series nature.

**Table: `chat_history`**
*   **Partition Key:** `conversation_id` (to keep one conversation's messages on the same node).
*   **Sort Key:** `timestamp`.
*   **Fields:** `message_id`, `sender_id`, `text`, `metadata` (intent identified, LLM tokens used).

### 3.3 Session Store (Redis)
Used for ephemeral state.
*   **Key:** `session:{bot_id}:{user_id}`
*   **Value:** JSON object containing current `flow_state`, `temporary_variables` (e.g., `cart_id`), and `last_interaction_time`.
*   **TTL:** 30 minutes to 24 hours.

### 3.4 Vector Database (Pinecone / Milvus)
Used for RAG.
*   **Index:** `bot_id` (Namespace).
*   **Vector:** Embedding of a document chunk.
*   **Metadata:** `source_url`, `text_chunk`.

---

## 4. Core API Design

### 4.1 Message Webhook (Ingress)
`POST /v1/bot/{bot_id}/messages`
*   **Request:**
    ```json
    {
      "user_id": "user_123",
      "channel": "whatsapp",
      "message": "I want to track my order",
      "timestamp": "2023-10-27T10:00:00Z",
      "payload": { "extra_channel_data": "..." }
    }
    ```
*   **Response:**
    ```json
    {
      "message_id": "msg_987",
      "response_text": "Sure! Please provide your order number.",
      "action": "WAIT_FOR_INPUT",
      "context": { "current_intent": "order_tracking" }
    }
    ```

### 4.2 Bot Configuration API (Management)
`PUT /v1/admin/bot/{bot_id}/config`
*   **Request:**
    ```json
    {
      "llm_provider": "gpt-4",
      "system_prompt": "You are a helpful assistant for a shoe store.",
      "temperature": 0.7,
      "knowledge_base_id": "kb_456"
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Caching Strategy
*   **Bot Config Cache:** Bot configurations are read-heavy and change rarely. Cache these in Redis with a TTL and use a "Cache-Aside" pattern.
*   **LLM Response Caching:** For common queries (e.g., "What are your hours?"), cache the LLM response based on a hash of the prompt to save costs and latency.

### 5.2 Message Queuing & Async Processing
*   **Analytics Pipeline:** Do not calculate analytics in the request path. Push every message event to **Kafka**. An analytics consumer will then aggregate data into a Data Warehouse (ClickHouse or Snowflake).
*   **Webhook Delivery:** When sending messages back to third-party APIs (like WhatsApp), use a retry queue with exponential backoff to handle external downtime.

### 5.3 Rate Limiting
*   **User Level:** Prevent a single user from spamming a bot (using Token Bucket algorithm in Redis).
*   **Bot Level:** Limit the total requests a business's bot can handle based on their subscription tier.

### 5.4 LLM Optimization
*   **Streaming:** Implement Server-Sent Events (SSE) or WebSockets to stream LLM responses to the user, reducing "perceived latency."
*   **Prompt Compression:** Truncate chat history to fit within the LLM context window, keeping only the most recent $N$ messages and a summary of the older conversation.

---

## 6. Trade-off Analysis

### 6.1 Consistency vs. Availability (CAP Theorem)
*   For **Chat History**, we prioritize **Availability and Partition Tolerance (AP)**. It is acceptable if a user sees a message slightly out of order or with a tiny delay, but the bot must never stop responding.
*   For **Bot Configuration**, we prioritize **Consistency (CP)**. If a business updates their bot's pricing logic, all users should see the updated logic as soon as possible.

### 6.2 Latency vs. Quality
*   **The LLM Dilemma:** Complex models (GPT-4) provide higher quality but higher latency.
*   **Solution:** A "Tiered Routing" approach. The Intent Engine (fast) handles 80% of common queries. The LLM (slow) handles the 20% complex long-tail queries.

### 6.3 SQL vs. NoSQL for History
*   **SQL:** Would allow complex queries (e.g., "Find all users who asked about X in June"), but would struggle with the write volume and scaling of billions of rows.
*   **NoSQL (Cassandra):** Offers linear scalability and high write throughput, which is critical for a platform with millions of concurrent messages. Complex analytics are offloaded to a dedicated OLAP system via Kafka.""",
}
