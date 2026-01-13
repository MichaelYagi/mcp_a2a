**Lessons Learned & Challenges Encountered**
============================================

This project has been a deep dive into how modern agentic systems actually work under the hood. Building my own MCP client exposed the real mechanics behind tool orchestration, schema enforcement, prompt routing, and networked agent workflows. Along the way, several themes emerged.

**Key Challenges Encountered**
------------------------------

### **1\. Never‑Ending Recursive Loops**

One of the most difficult problems I ran into was the emergence of recursive loops where the client and the LLM would continuously respond to each other without making progress. This usually happened when:

-   the router prompt misclassified the user's intent

-   the LLM attempted to "fix" its own previous output

-   the client interpreted the LLM's response as a new request

-   the system re‑entered the same reasoning path over and over

These loops were subtle, hard to detect, and even harder to break once they started. They exposed how fragile agentic workflows can be when the boundaries between "LLM reasoning" and "client logic" aren't clearly enforced. It taught me that **orchestration must be explicit**, not emergent.

### **2\. Hard‑Coded Keywords Are Not a Real Solution**

To stop the loops, I rely on hard‑coded keywords to detect when the LLM was drifting into unwanted behavior. While this worked as a temporary patch, it quickly became clear that:

-   keyword checks are brittle

-   they don't scale

-   they break easily when prompts evolve

-   they force the LLM to conform to arbitrary phrasing

-   they create hidden dependencies between prompts and client logic

This approach solved the symptom, not the underlying problem. The real fix required:

-   clearer tool schemas

-   stricter validation

-   more explicit routing logic

-   better separation between agent roles

-   deterministic client‑side control over execution flow

These changes made the system far more stable than any keyword‑based guardrail could.

### **3\. LLM Hallucinations Created Unreliable and Unsafe Tool Calls**

Another major challenge was the frequency and severity of hallucinations during tool execution. The LLM would often:

-   invent fields that didn't exist in the schema

-   omit required arguments

-   guess at values instead of using retrieved data

-   fabricate metadata or media IDs

-   confidently output invalid JSON

-   "assume" tool behavior that didn't match reality

These hallucinations weren't just cosmetic --- they broke workflows, corrupted ingestion, and triggered recursive loops. They made it clear that **LLMs cannot be trusted as authoritative sources of structure or truth** without strict guardrails.

This forced several architectural decisions:

-   **schema validation became mandatory**, not optional

-   **tool arguments had to be validated before execution**

-   **routing logic had to be explicit**, not inferred

-   **the client had to own control flow**, not the model

-   **prompts had to be domain‑specific** to reduce ambiguity

Hallucinations were a constant reminder that an MCP client must treat the LLM as a *probabilistic assistant*, not a deterministic component. The system only became stable once the client enforced structure, validated inputs, and constrained the model's freedom to invent.


**Challenges Encountered**
--------------------------

### **1\. WebSocket reliability**

Building a stable WebSocket client/server pair surfaced issues like:

-   dropped connections

-   partial frames

-   reconnection logic

-   race conditions during shutdown

These problems don't appear in simple examples but show up immediately in real workflows.

### **2\. Schema validation wasn't optional**

LLMs frequently produced:

-   missing fields

-   wrong types

-   invented arguments

-   malformed JSON

Without strict schema validation, tools would have behaved unpredictably.

### **3\. Tool routing required careful design**

The router prompt had to:

-   classify intent

-   select the correct domain agent

-   avoid unnecessary tool calls

-   prevent loops

-   handle errors gracefully

This was one of the most iterative parts of the project.

### **4\. LAN‑accessible UI introduced new constraints**

Once the UI was accessible across devices, I had to think about:

-   cross‑origin requests

-   session persistence

-   network latency

-   browser reconnection behavior

-   security boundaries

Local‑only assumptions no longer held.

### **5\. Debugging LLM behavior required instrumentation**

To understand why an agent made a decision, I needed:

-   logging

-   validation errors

-   raw tool call traces

-   router decisions

-   intermediate reasoning

Without observability, debugging would have been guesswork.

**Lessons Learned**
-------------------

### **1\. MCP is complex in practice**

The protocol itself is small and elegant, but implementing a real client revealed how much hidden work is involved:

-   message framing

-   WebSocket lifecycle management

-   tool routing

-   schema validation

-   error propagation

-   state synchronization

Understanding these pieces gave me a much clearer mental model of how clients like Claude Desktop operate behind the scenes.

### **2\. Deterministic tool execution requires explicit design**

LLMs are flexible, but that flexibility becomes a liability without guardrails. I learned that:

-   tools must be validated

-   arguments must be schema‑checked

-   routing must be explicit

-   retries must be intentional

Determinism doesn't happen automatically --- it's engineered.

### **3\. Multi‑prompt architectures dramatically improve reliability**

Splitting responsibilities across domain‑specific prompts (media, summarization, KB search, code review) made the system:

-   easier to debug

-   more predictable

-   less prone to hallucination

-   easier to extend

Even when everything runs sequentially, specialization matters.

### **4\. Server‑authoritative state is essential for consistency**

Letting the backend own the chat history and session state ensures:

-   perfect alignment between UI and server

-   reproducible workflows

-   no hidden client‑side mutations

This was especially important once I exposed the UI over the LAN.

### **5\. RAG pipelines are only as good as their ingestion**

Subtitle ingestion taught me that:

-   chunking matters

-   metadata matters

-   embedding consistency matters

-   ingestion must be automated

A media intelligence system is only as strong as its data hygiene.

### **6\. Networking is always more complicated than expected**

Exposing the agent UI and webhook endpoints across devices required:

-   portproxy

-   firewall rules

-   WSL networking quirks

-   LAN IP routing

-   hostname stability

It reinforced that distributed systems always introduce friction.

**Summary**
-----------

This project has been as much about learning the architecture of agentic systems as it has been about building one. The challenges --- networking, schema enforcement, routing, ingestion, and orchestration --- forced me to understand the real mechanics behind MCP clients, LLM‑driven workflows, and distributed tool ecosystems. The result is a system that's modular, deterministic, observable, and ready for future expansion.