### **1. Intro – Setting the Stage (±5 min)**

**Goal:** Hook attention and create context.

* Open with: “We’ve all seen AI demos — impressive, but rarely useful in day-to-day work.”
* The current reality: most AI tools stop at text generation; few connect to *actual systems*.
* Introduce MCP as the **missing bridge** between AI and your existing company tools and data.
* Preview: “Today I’ll show you what MCP is, why it matters, and how you can go from zero to a working AI tool in under a day.”

---

### **2. The Problem – Why MCP Matters (±5 min)**

**Goal:** Create urgency by illustrating the gap.

* LLMs can *think* — but they can’t *act*.
* Companies already have valuable APIs, data, and workflows — but those live in isolation.
* Without a bridge, AI stays abstract.
* “We don’t need another chatbot — we need useful ones that actually do things.”

---

### **3. Introducing MCP – The Bridge (±8–10 min)**

**Goal:** Explain MCP simply and build understanding.

* **Definition:** Model Context Protocol — a standard for connecting AI models to tools and data.
* **Analogy:** A *universal adapter* for AI — allowing models to use APIs like power tools.
* **Core benefits:**

  * Open and community-driven
  * Simple JSON spec
  * Works with multiple models (Claude, OpenAI, etc.)
  * Privacy-friendly and local
* **Examples of existing MCP servers you can try today:**

  * [**Context7**](https://context7.ai) – file and document operations
  * **Figma MCP Server** – design collaboration
  * **Jira MCP Server** – project management integration
  * *(Plus many more on the official [MCP Registry](https://github.com/modelcontextprotocol/registry))*

---

### **4. What Makes MCP Different (±5 min)**

**Goal:** Clarify the “why now” — and why this isn’t just another fad.

* **Before MCP:**

  * Each platform had its own plugin system (ChatGPT, Claude, Copilot, etc.)
  * Tools were siloed and hard to maintain.
* **With MCP:**

  * One shared protocol — *build once, use anywhere*.
  * Adopted rapidly by the community.
* **Big players are moving fast:**

  * Salesforce → adding MCP support to Einstein AI integrations
  * Microsoft → experimenting with MCP-like connectors in Copilot
  * Google → exploring open tool standards for Workspace & Gemini
* **Key message:** MCP isn’t another shiny app — it’s *standardization*, the boring-but-powerful kind that unlocks ecosystems.

---

### **5. Demo – From API to MCP Tool (±15 min)**

**Goal:** Make it tangible, fast-paced, and inspiring.

* **Context:**
  “This is a small project I built in less than a day, using Claude Code inside [Vibecoded](https://vibecoded.com). It’s a full working prototype — and I want to show how easy it is to go from API to working MCP tools.”
* **Live steps:**

  1. Upload OpenAPI spec
  2. Convert endpoints into tools (with LLM-enriched descriptions)
  3. Combine endpoints into composite tools for real use cases
  4. Generate the tools spec (JSON)
  5. Download a small Python MCP server
  6. Run it locally and test in Claude Desktop
* **Key message:**

  * “I didn’t write everything by hand — I co-built this with AI in a few hours.”
  * “If you can describe your use case, you can build an MCP tool.”
* ⚠️ **Important nuance:**

  * Most existing APIs need adaptation — descriptions, structure, parameters — to work well as MCP tools.
  * This is where AI-assisted enrichment shines: making your APIs *AI-friendly* and usable.

---

### **6. What This Means – Possibilities & Next Steps (±5 min)**

**Goal:** Zoom out and connect to strategy.

* **Opportunities:**

  * Internal use: smarter automations, instant data access
  * Client work: new value-added AI integrations
  * Partnerships: create reusable MCP tools for shared clients
* **Risks & lessons:**

  * Security, governance, and API hygiene matter
  * Tools must be clear, safe, and purposeful
* **Momentum:**
  MCP is quickly becoming the *default layer* between AI models and business systems — like what REST or GraphQL did for web apps.

---

### **7. Outro & Q&A (±5–10 min)**

**Goal:** Leave them energized and curious.

* Recap:
  “Met MCP-tools maak je AI écht bruikbaar — met wat je vandaag al hebt.”
* Emphasize accessibility:

  * You can try existing servers today (see MCP Registry)
  * You can build your own tomorrow — even without deep coding skills
* Call to action:
  “Don’t wait for vendors to integrate this — start experimenting. The barrier has never been this low.”
* Open floor for questions or ideas.
