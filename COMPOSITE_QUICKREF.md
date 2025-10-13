# Composite Tool Quick Reference

## Setup

```bash
# Required environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# Your API key
export API_KEY=your-api-key
```

## How It Works

```
┌─────────────────────────────────────────────────┐
│  User calls composite tool                      │
│  get_customer_with_latest_products(id="123")    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Server creates Claude agent with:              │
│  • Orchestration logic from tools.json          │
│  • All standard tools as callable functions     │
│  • User input parameters                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Agent Loop (max 20 iterations):                │
│                                                 │
│  Claude decides: "Need to get customer first"   │
│    → Calls getCustomer(customerId="123")        │
│    ← {id: "123", name: "John", ...}             │
│                                                 │
│  Claude: "Now get their orders"                 │
│    → Calls listCustomerOrders(id="123")         │
│    ← {orders: [{productIds: ["p1","p2"]}, ...]} │
│                                                 │
│  Claude: "Extract product IDs and get details"  │
│    → Calls getProduct(productId="p1")           │
│    → Calls getProduct(productId="p2")           │
│    ...                                          │
│                                                 │
│  Claude: "Combine all results"                  │
│    → Returns final aggregated response          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  User receives complete result:                 │
│  {                                              │
│    customer: {...},                             │
│    products: [...]                              │
│  }                                              │
└─────────────────────────────────────────────────┘
```

## Example Composite Tool

```json
{
  "name": "get_customer_with_latest_products",
  "description": "Get customer and their latest 10 products",
  "orchestration_logic": "1) Get customer by ID 2) Get customer's orders (limit 10) 3) Extract product IDs from orders 4) Get product details for each ID 5) Combine customer + products",
  "input_schema": {
    "type": "object",
    "properties": {
      "customerId": { "type": "string" }
    },
    "required": ["customerId"]
  }
}
```

## Execution Log

```
[MCP] Executing composite tool: get_customer_with_latest_products
[MCP] Starting LLM orchestration agent...
[MCP] Agent iteration 1/20
[MCP]   → Calling tool: getCustomer({"customerId": "123"})
[MCP]   ← Result: Status: 200 ...
[MCP] Agent iteration 2/20
[MCP]   → Calling tool: listCustomerOrders({"customerId": "123", "limit": 10})
[MCP]   ← Result: Status: 200 ...
[MCP] Agent completed successfully in 12 iterations
```

## Key Features

✅ **Intelligent ordering** - LLM figures out correct sequence
✅ **Data extraction** - Pulls IDs/values from responses
✅ **Dynamic iteration** - Loops over results (e.g., each product)
✅ **Error handling** - Adapts if calls fail
✅ **Self-documenting** - Orchestration logic explains what happens

## Costs

- ~$0.01-0.05 per execution
- Depends on complexity and number of API calls
- Uses Claude 3.5 Sonnet

## Debugging

1. Check logs for each agent iteration
2. See which tools are called and their results
3. Verify orchestration logic is clear
4. Ensure ANTHROPIC_API_KEY is set

## Common Issues

### "Composite tools require ANTHROPIC_API_KEY"
→ Set the environment variable

### Agent hits max iterations (20)
→ Orchestration logic may be unclear
→ Try simplifying or adding more detail

### Wrong order of API calls
→ The agent decides order based on logic
→ Update orchestration_logic to be more explicit

## When to Use

**Use composite tools when:**
- Need to call multiple endpoints
- Data from one call feeds into another
- Need to loop over results
- Need to aggregate/combine data

**Don't use composite tools when:**
- Single endpoint is sufficient
- No data dependencies
- Simple sequential calls
- Cost is a major concern

## See Also

- [COMPOSITE_SOLUTION.md](COMPOSITE_SOLUTION.md) - Full implementation details
- [COMPOSITE_TOOL_ORCHESTRATION.md](COMPOSITE_TOOL_ORCHESTRATION.md) - Architecture docs
