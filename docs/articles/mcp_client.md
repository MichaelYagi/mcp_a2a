**Why Build My Own MCP Client?**
==================================

It started with using Claude Desktop as a client (which you can still do), but building one out on my own was a learning experience, in addition other several reasons. First, I wanted a deeper understanding of how MCP clients actually work behind the scenes — not just how they behave from the outside, but how they orchestrate messages, manage state, and coordinate tool execution. 

Second, I wanted hands‑on experience with the technologies and techniques involved in building a real client: Schema validation, routing logic, system and tool prompts, and deterministic tool handling. 

Finally, I wanted to explore the architecture that connects the three core components of any agentic system — the server, the LLM, and the client — and understand how they communicate, where responsibilities should live, and how to design a system that is modular, observable, and extensible. 

*An overview of the advantages demonstrated in this project.*

The benefits come directly from the systems implemented here: deterministic tool execution, multi‑prompt routing, Plex automation, RAG integration, LAN access, and strict validation.

Deterministic Tool Execution
-------------------------------

The client controls the entire lifecycle of a tool call:

-   explicit sequencing

-   predictable retries

-   error handling

-   no hidden LLM decisions

This ensures stable, reproducible behavior and important for ingestion pipelines and media workflows.

Modular, Extensible Tool Suite
---------------------------------

Tools in this project are:

-   domain‑specific (Plex, Weather APIs, knowledge base, to-do's, text summarization)

-   cleanly separated

-   versioned

-   easy to extend

The client enforces schemas and validation, ensuring tools behave consistently across workflows.

Multi‑Prompt Architecture
----------------------------

Instead of one giant prompt, the system uses a **router prompt** which allows for domain‑specific prompts for media, summarization, KB search, code review, and other tools.

This gives each domain its own reasoning style and constraints, improving accuracy and reducing hallucinations.

Server‑Authoritative Chat History
-------------------------------------

The client maintains:

-   synchronized history

-   backend‑controlled state

-   alignment between UI and server

-   reproducible sessions

This avoids the opaque, UI‑bound history model of desktop clients.

LAN‑Accessible Agent UI
--------------------------

The client exposes a browser UI across your home network, enabling:

-   cross‑device access

-   friendly hostnames

-   portproxy routing

-   firewall‑aware connectivity

This turns the agent into a household service rather than a single‑machine app.

Debugging, Logging, and Validation
-------------------------------------

The client provides:

-   strict schema validation

-   detailed logging

-   transparent tool calls

-   error‑aware routing

-   guardrails against hallucination

This makes the system observable and debuggable - something desktop clients don't expose.

Integrated Plex + RAG
-----------------------------------

The client orchestrates:

-   Plex webhook ingestion

-   subtitle extraction

-   embedding and vector storage

-   metadata enrichment

-   retrieval for media queries

This creates a self‑updating media knowledge base - a workflow impossible to run inside a desktop‑only agent.

Clean, Reproducible Workflows
--------------------------------

The system ensures:

-   consistent behavior

-   predictable outputs

-   no hidden agent decisions

-   no UI‑driven side effects

This aligns with an engineering style focused on clarity, reproducibility, and maintainability.

**Summary**
===========

Building your own MCP client gives you:

-   deterministic tool execution

-   modular prompts and tools

-   server‑controlled history

-   LAN‑accessible UI

-   integrated Plex + RAG automation

-   strict validation and debugging

-   domain‑specific reasoning

-   a foundation for multi‑agent workflows

These advantages come directly from the systems implemented in this project.