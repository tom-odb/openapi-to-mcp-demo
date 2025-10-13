# Composite Tool Solution: MCP Tool Orchestration with LLM

## Problem Identified

The original composite tool implementation was too simplistic:
- ❌ Just executed endpoints sequentially
- ❌ No data flow between calls
- ❌ Couldn't extract data from responses
- ❌ No dynamic iteration
- ❌ Endpoints in wrong order in tools.json
- ❌ Can't handle complex orchestration

**Example:** `get_customer_with_latest_products` needs to:
1. Get customer details
2. Get customer's orders
3. Extract product IDs from orders
4. Call `/products/{id}` for EACH product ID (dynamic iteration)
5. Aggregate results

The simple sequential approach can't do this.

## Solution Implemented

### MCP Tool Orchestration with LLM

The composite tool handler uses **Claude to orchestrate MCP tool calls**:

✅ **MCP tools are the primitives** - Each API endpoint is an MCP tool
✅ **Claude orchestrates MCP tools** - LLM decides which MCP tools to call
✅ **Demonstrates MCP patterns** - Shows MCP server using MCP tools internally
✅ **Handles complexity** - Data flow, iteration, aggregation all work

### Architecture: MCP Tools as Building Blocks

```
┌─────────────────────────────────────────┐
│  MCP Server (this server)               │
│                                         │
│  Composite Tool Handler:                │
│  ┌─────────────────────────────────┐   │
│  │  Claude Orchestration Agent     │   │
│  │  • Given MCP tool definitions   │   │
│  │  • Calls MCP tools via          │   │
│  │    standard tool handler        │   │
│  │  • Each tool = API endpoint     │   │
│  └─────────────────────────────────┘   │
│           ↓                             │
│  Standard MCP Tools:                    │
│  • getCustomer (MCP tool)               │
│  • listCustomerOrders (MCP tool)        │
│  • getProduct (MCP tool)                │
│  • ... (all are MCP tools)              │
│           ↓                             │
│  → Make HTTP calls to actual API        │
└─────────────────────────────────────────┘
```

**This IS MCP!** The composite tool orchestrates **other MCP tools** (the standard endpoint tools).

### How It Works

```
User: get_customer_with_latest_products(customerId="123")
    ↓
Composite tool handler creates orchestration agent with:
  - MCP tool definitions (standard tools)
  - Orchestration logic
  - User input
    ↓
Claude orchestrates MCP tool calls:
  Iteration 1: "I need customer details"
    → Calls MCP tool: getCustomer(customerId="123")
    ← MCP tool returns: {id: "123", name: "John", ...}
  
  Iteration 2: "Now get their orders"
    → Calls MCP tool: listCustomerOrders(customerId="123")
    ← MCP tool returns: {orders: [...]}
  
  Iteration 3-12: "Get each product"
    → Calls MCP tool: getProduct(productId="p1")
    → Calls MCP tool: getProduct(productId="p2")
    ... (multiple MCP tool calls)
  
  Final: "Combine results"
    → Returns aggregated response
    ↓
User gets complete result
```

**Key MCP Concept:** The composite tool is essentially **an MCP tool that orchestrates other MCP tools**!

## Why This IS an MCP Pattern

### MCP Tools Calling MCP Tools

The implementation demonstrates a key MCP pattern:

1. **Standard tools are MCP tools** - Each API endpoint is exposed as an MCP tool
2. **Composite tool is an MCP tool** - It's exposed via the same MCP interface
3. **Composite tool uses MCP tools** - It internally calls the standard MCP tools
4. **LLM orchestrates MCP tools** - Claude decides which MCP tools to call

This is **MCP tool composition** - higher-level MCP tools built from lower-level MCP tools!

### MCP Benefits Demonstrated

✅ **Tool Reusability** - Standard MCP tools work standalone OR in compositions
✅ **Declarative Composition** - Composite tools defined in JSON, not code
✅ **Flexible Orchestration** - LLM provides intelligent tool sequencing
✅ **Type Safety** - All tools use JSON Schema for inputs
✅ **Protocol Native** - Everything goes through MCP tool call mechanism

### 1. Updated generic_server.py

**Added:**
- `from anthropic import Anthropic`
- `self.anthropic_api_key` from environment
- New `_handle_composite_tool()` implementation using agentic loop
- Logging for orchestration steps

**Agent Loop:**
- Creates Claude client
- Iterates up to 20 times
- Passes system prompt with orchestration logic
- Gives Claude access to all standard tools
- Claude calls tools via tool use
- Server executes tools and returns results
- Loop continues until Claude returns final answer

### 2. Updated Dependencies

**pyproject.template.toml:**
```toml
dependencies = [
    "mcp>=0.9.0",
    "httpx>=0.26.0",
    "python-dotenv>=1.0.0",
    "anthropic>=0.39.0"  # NEW
]
```

### 3. Updated Environment Config

**.env.template:**
```bash
API_KEY=your-api-key
ANTHROPIC_API_KEY=your-anthropic-key  # NEW - Required for composite tools
```

### 4. New Documentation

**COMPOSITE_TOOL_ORCHESTRATION.md:**
- Explains the problem and solution
- Shows execution flow
- Documents configuration
- Cost considerations
- Logging examples
- Testing instructions

## Benefits

### ✅ Solves Complex Orchestration
- Handles data flow between calls
- Dynamic iteration over results
- Intelligent ordering of calls
- Data extraction and transformation

### ✅ No Code Generation
- Uses orchestration logic as guidance
- LLM figures out the implementation
- Adapts to different response structures

### ✅ Robust
- Works even if endpoints are in wrong order
- Handles API changes gracefully
- Self-correcting (LLM can retry)

### ✅ Maintainable
- No generated orchestration code
- Just declarative logic in JSON
- Easy to understand and debug

## Tradeoffs

### Costs
- Each composite tool uses Claude API
- ~$0.01-0.05 per execution (depending on complexity)
- More API calls = higher cost

### Latency
- Multiple round trips to Claude
- Sequential execution (not parallel)
- Slower than pre-generated code

### Dependency
- Requires ANTHROPIC_API_KEY
- Won't work offline
- Relies on Claude's availability

## Example Output

```bash
[MCP] Executing composite tool: get_customer_with_latest_products
[MCP] Use case: Retrieve customer with latest 10 products ordered
[MCP] Orchestration: 1) Get customer 2) Get orders 3) Extract IDs...
[MCP] Starting LLM orchestration agent...
[MCP] Agent iteration 1/20
[MCP]   → Calling tool: getCustomer({"customerId": "123"})
[MCP]   ← Result: Status: 200 {"id": "123", "name": "John Doe"}...
[MCP] Agent iteration 2/20
[MCP]   → Calling tool: listCustomerOrders({"customerId": "123", "limit": 10})
[MCP]   ← Result: Status: 200 {"orders": [{"orderId": "o1", "productIds": ["p1", "p2"]}]}...
[MCP] Agent iteration 3/20
[MCP]   → Calling tool: getProduct({"productId": "p1"})
[MCP]   ← Result: Status: 200 {"id": "p1", "name": "Widget", "price": 19.99}...
... (continues for each product)
[MCP] Agent completed successfully in 12 iterations
```

## Alternatives Considered

### ❌ Generate Orchestration Code
- **Problem:** Too brittle, hard to maintain
- **Issue:** Need to handle every possible data flow pattern
- **Verdict:** Would defeat the declarative architecture

### ❌ Simple Sequential Execution
- **Problem:** Can't handle data flow
- **Issue:** No way to extract data from one call to use in the next
- **Verdict:** Only works for trivial cases

### ❌ Workflow Engine (Temporal, Airflow, etc.)
- **Problem:** Too complex for this use case
- **Issue:** Massive dependency, overkill
- **Verdict:** Wrong tool for the job

### ✅ LLM Agent Orchestration
- **Benefit:** Perfect balance of flexibility and simplicity
- **Benefit:** Leverages AI for intelligent orchestration
- **Verdict:** Best solution for dynamic, complex workflows

## Migration

For existing composite tools:
1. Ensure `ANTHROPIC_API_KEY` is set in environment
2. Regenerate server (or just copy new `server.py`)
3. Update `pyproject.toml` to include `anthropic` dependency
4. Run `uv sync` or `pip install -e .`
5. Test composite tools

## Future Enhancements

1. **Parallel Execution** - Allow agent to call multiple tools concurrently
2. **Streaming** - Stream partial results as they arrive
3. **Cost Optimization** - Use cheaper models for simple cases
4. **Caching** - Cache intermediate results
5. **Hybrid Mode** - Use simple execution for trivial cases, LLM for complex ones
6. **Custom Scripts** - Allow Python code for deterministic orchestrations

## Summary

**Problem:** Composite tools need intelligent orchestration with data flow

**Solution:** Use Claude as an on-the-fly orchestration agent

**Result:** 
- ✅ Complex workflows work correctly
- ✅ No code generation needed
- ✅ Declarative architecture preserved
- ✅ Self-documenting and maintainable

**Trade-off:** Small cost per execution (~$0.01-0.05) for massive flexibility
