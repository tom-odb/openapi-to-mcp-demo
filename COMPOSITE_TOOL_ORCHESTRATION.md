# Composite Tool Orchestration with MCP

## The Problem

Composite tools need to:
- Execute multiple API endpoints in the correct order
- Extract data from one response to use in the next call
- Handle dynamic iteration (e.g., call `/products/{id}` for each product ID found)
- Aggregate and transform results
- Deal with varying response structures

A simple sequential execution won't work because it can't handle data flow between calls.

## The Solution: MCP Tool Orchestration

Instead of trying to generate orchestration code, we use **MCP tools as the building blocks** and **Claude to orchestrate them**:

1. **Each API endpoint is an MCP tool** - Standard tools expose individual endpoints
2. **Composite tools are also MCP tools** - Higher-level tools exposed via MCP
3. **Claude orchestrates MCP tool calls** - LLM decides which MCP tools to call
4. **This demonstrates MCP composition** - MCP tools built from other MCP tools

### MCP Pattern: Tool Composition

```
┌─────────────────────────────────────┐
│  User calls composite MCP tool      │
│  get_customer_with_latest_products  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  MCP Server handles composite tool  │
│  • Receives MCP tool call           │
│  • Starts orchestration             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Claude orchestrates MCP tools:     │
│  • Calls getCustomer (MCP tool)     │
│  • Calls listCustomerOrders (MCP)   │
│  • Calls getProduct (MCP) × N       │
│  • Each call goes through standard  │
│    MCP tool handler                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Returns aggregated result via MCP  │
└─────────────────────────────────────┘
```

**This IS MCP!** We're not using a separate tool-use API - we're using **MCP tools to orchestrate other MCP tools**.

## How It Works

### 1. Composite Tool Structure

```json
{
  "name": "get_customer_with_latest_products",
  "description": "Get customer details with their latest products",
  "use_case_description": "Retrieve customer with latest 10 products ordered",
  "orchestration_logic": "1) Get customer details 2) Get customer orders 3) Extract product IDs 4) Get product details 5) Combine results",
  "input_schema": {
    "type": "object",
    "properties": {
      "customerId": { "type": "string" }
    }
  },
  "endpoint_mappings": [
    // List of endpoints that MIGHT be needed (agent decides which to use)
  ]
}
```

### 2. Agent Execution Flow

```
User calls composite tool
    ↓
Server creates LLM agent with:
  - System prompt with orchestration logic
  - Access to all standard API tools
  - User input parameters
    ↓
Agent iteratively:
  1. Decides which tool to call next
  2. Calls the tool via the server
  3. Receives the response
  4. Extracts needed data
  5. Repeats until task complete
    ↓
Agent returns final aggregated result
```

### 3. Example Execution

For `get_customer_with_latest_products(customerId="123")`:

**Iteration 1:** Agent calls `getCustomer(customerId="123")`
- Response: `{"id": "123", "name": "John Doe", ...}`

**Iteration 2:** Agent calls `listCustomerOrders(customerId="123", limit=10)`
- Response: `{"orders": [{"id": "ord1", "productIds": ["p1", "p2"]}, ...]}`

**Iteration 3:** Agent extracts unique product IDs: `["p1", "p2", "p3", ...]`

**Iterations 4-13:** Agent calls `getProduct(productId=...)` for each product
- Aggregates product details

**Final:** Agent combines customer + products and returns result

## Advantages

✅ **Intelligent orchestration** - LLM figures out the right sequence
✅ **Handles data flow** - Extracts and passes data between calls
✅ **Dynamic iteration** - Can loop over results
✅ **Robust to API changes** - Adapts to different response structures
✅ **No code generation** - Uses the orchestration logic as guidance
✅ **Self-documenting** - The orchestration logic explains what happens

## Configuration

### Environment Variables

```bash
# Required for composite tools
ANTHROPIC_API_KEY=sk-ant-...

# Your API credentials
API_KEY=your-api-key
```

### Cost Considerations

Each composite tool execution uses Claude API calls:
- Input tokens: ~500-2000 (system prompt + tool definitions)
- Output tokens: Varies based on complexity
- Tool calls: Number of API endpoints called

For the customer+products example:
- ~1 Claude call per API endpoint
- ~10-15 API calls total
- Cost: ~$0.01-0.05 per execution

## Logging

The server logs each step:

```
[MCP] Executing composite tool: get_customer_with_latest_products
[MCP] Use case: Retrieve customer with latest 10 products ordered
[MCP] Orchestration: 1) Get customer details 2) Get customer orders...
[MCP] Starting LLM orchestration agent...
[MCP] Agent iteration 1/20
[MCP]   → Calling tool: getCustomer({"customerId": "123"})
[MCP]   ← Result: Status: 200 {"id": "123", "name": "John"}...
[MCP] Agent iteration 2/20
[MCP]   → Calling tool: listCustomerOrders({"customerId": "123", "limit": 10})
[MCP]   ← Result: Status: 200 {"orders": [...]}...
...
[MCP] Agent completed successfully in 12 iterations
```

## Limitations

- **Requires ANTHROPIC_API_KEY** - Won't work without it
- **Cost per execution** - Each composite tool uses Claude API
- **Max 20 iterations** - Prevents infinite loops
- **Latency** - Multiple round trips to Claude + API calls
- **No parallel execution** - Calls are sequential

## Fallback for Simple Cases

If a composite tool is truly simple (just 2-3 sequential calls with no data flow), you might want to implement a simple mode. But for complex orchestration like the customer+products example, the LLM agent is essential.

## Testing

To test composite tools:

1. Set `ANTHROPIC_API_KEY` in environment
2. Call the composite tool via MCP
3. Watch the logs to see the orchestration
4. Verify the final result includes all expected data

## Alternative Approaches Considered

❌ **Generate orchestration code** - Too brittle, hard to maintain
❌ **Simple sequential execution** - Can't handle data flow
❌ **Hardcode each composite tool** - Defeats the purpose
❌ **Use workflow engines** - Too complex for this use case
✅ **LLM agent orchestration** - Perfect balance of flexibility and simplicity

## Future Enhancements

- **Parallel execution** - Allow agent to call multiple tools concurrently
- **Caching** - Cache intermediate results
- **Cost optimization** - Use cheaper models for simple orchestrations
- **Streaming responses** - Stream partial results as they arrive
- **Custom orchestration scripts** - Allow Python code for deterministic cases
