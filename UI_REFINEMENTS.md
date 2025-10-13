# UI Refinements: Tool Selection & Unified Configuration

## Changes Made

### 1. Removed Separate Tool Preview Step

**Before:** 4-step workflow
- Step 1: Upload Spec
- Step 2: Enrich Endpoints
- Step 3: Composite Tools
- Step 4: Generate Tools (with API config)
- Step 5: Download Server

**After:** Streamlined 4-step workflow
- Step 1: Upload Spec
- Step 2: Enrich Endpoints
- Step 3: Composite Tools
- Step 4: Generate Server (includes API config + tool selection)

### 2. Added Tool Selection to Server Generator

Users can now:
- ✅ Select which standard tools to include
- ✅ Select which composite tools to include
- ✅ See tool descriptions and endpoint mappings
- ✅ Select/deselect all with one click
- ✅ All tools selected by default

### 3. Moved API Configuration to Server Generator

The API configuration (API name and base URL) is now in the final step alongside:
- Server name configuration
- Tool selection
- Server generation

This eliminates an unnecessary intermediate step.

## UI Components

### ServerGenerator.vue - New Features

#### API Configuration Section
```vue
<div class="config-section">
  <h3>API Configuration</h3>
  <input v-model="apiName" placeholder="e.g., my-api" />
  <input v-model="baseUrl" placeholder="e.g., https://api.example.com" />
</div>
```

#### Server Configuration Section
```vue
<div class="config-section">
  <h3>Server Configuration</h3>
  <input v-model="serverName" placeholder="e.g., my-api-mcp" />
</div>
```

#### Tool Selection Section
```vue
<div class="config-section">
  <h3>Select Tools to Include</h3>
  
  <!-- Composite Tools -->
  <div class="tool-section">
    <h4>Composite Tools ({{ store.compositeTools.length }})</h4>
    <label v-for="tool in store.compositeTools" class="tool-checkbox">
      <input type="checkbox" v-model="selectedCompositeTools" />
      <div class="tool-info">
        <span class="tool-name">{{ tool.name }}</span>
        <span class="badge composite">Composite</span>
        <p>{{ tool.description }}</p>
      </div>
    </label>
  </div>
  
  <!-- Standard Tools -->
  <div class="tool-section">
    <h4>Standard Tools ({{ store.endpoints.length }})</h4>
    <label v-for="endpoint in store.endpoints" class="tool-checkbox">
      <input type="checkbox" v-model="selectedStandardTools" />
      <div class="tool-info">
        <span class="tool-name">{{ getToolName(endpoint) }}</span>
        <span class="endpoint-badge">{{ endpoint.method }} {{ endpoint.path }}</span>
        <p>{{ endpoint.enriched_description }}</p>
      </div>
    </label>
  </div>
  
  <!-- Selection Actions -->
  <button @click="selectAllTools">Select All</button>
  <button @click="deselectAllTools">Deselect All</button>
</div>
```

## Logic Changes

### Tool Filtering

When generating the server, only selected tools are included:

```javascript
const filteredToolModel = {
  ...store.toolModel,
  tools: store.toolModel.tools.filter(tool => {
    // Check if this tool's endpoint is selected
    const endpoint = store.endpoints.find(e => 
      e.path === tool.endpoint_mapping.path && 
      e.method === tool.endpoint_mapping.method
    )
    return endpoint && selectedStandardTools.value.includes(`${endpoint.path}:${endpoint.method}`)
  }),
  composite_tools: (store.toolModel.composite_tools || []).filter(tool => 
    selectedCompositeTools.value.includes(tool.name)
  )
}
```

### Workflow

1. User reaches Server Generator step
2. All tools are selected by default
3. User can deselect unwanted tools
4. User enters API config (name, base URL)
5. User enters server name
6. Click "Generate Server Package"
7. System:
   - Generates tool definitions with API config
   - Filters to only selected tools
   - Generates server package
   - Provides download

## UI Improvements

### Visual Hierarchy

```
┌─────────────────────────────────────┐
│ Generate MCP Server                 │
│ Configure API and select tools      │
├─────────────────────────────────────┤
│                                     │
│ ┌─ API Configuration ─────────────┐│
│ │ • API Name: [input]             ││
│ │ • Base URL: [input]             ││
│ └─────────────────────────────────┘│
│                                     │
│ ┌─ Server Configuration ──────────┐│
│ │ • Server Name: [input]          ││
│ └─────────────────────────────────┘│
│                                     │
│ ┌─ Select Tools to Include ───────┐│
│ │ Composite Tools (2)             ││
│ │ ☑ get_customer_with_products    ││
│ │ ☑ create_order_with_items       ││
│ │                                  │
│ │ Standard Tools (10)              │
│ │ ☑ listProducts                   │
│ │ ☑ getProduct                     │
│ │ ☑ createProduct                  │
│ │ ...                              │
│ │                                  │
│ │ [Select All] [Deselect All]     ││
│ └─────────────────────────────────┘│
│                                     │
│ [Generate Server Package]           │
└─────────────────────────────────────┘
```

### Styling

- **Checkboxes**: Styled with hover effects
- **Tool cards**: White background with borders
- **Badges**: Color-coded (purple for composite, gray for endpoints)
- **Sections**: Separated with borders and backgrounds
- **Scrollable list**: Max height for long tool lists
- **Disabled state**: Clear visual feedback

## Benefits

### 1. Fewer Steps
- Reduced from 5 to 4 steps
- More streamlined user experience
- Less clicking and navigation

### 2. Better Control
- Users can exclude tools they don't need
- Smaller, more focused MCP servers
- Reduces tool clutter in Claude Desktop

### 3. Unified Configuration
- All server settings in one place
- Easier to review before generation
- Single point of configuration

### 4. Better UX
- All tools selected by default (sensible default)
- Quick select/deselect all
- Visual feedback for selections
- Tool descriptions visible during selection

## Testing Checklist

- [ ] Navigate to Server Generator step
- [ ] Verify all tools are selected by default
- [ ] Deselect some tools
- [ ] Click "Select All" - all tools should be selected
- [ ] Click "Deselect All" - no tools should be selected
- [ ] Enter API name and base URL
- [ ] Enter server name
- [ ] Generate server with partial tool selection
- [ ] Verify generated tools.json only contains selected tools
- [ ] Download and test the server package

## Future Enhancements

1. **Search/Filter**: Add search box to filter tools by name/description
2. **Grouping**: Group standard tools by resource (products, orders, etc.)
3. **Dependencies**: Show which composite tools depend on which standard tools
4. **Preview**: Show tool count and estimated server size
5. **Presets**: Save/load tool selection presets
6. **Bulk Actions**: Select all composite tools, select all GET endpoints, etc.

## Files Modified

- `frontend/src/components/ServerGenerator.vue` - Complete rewrite with tool selection
- `frontend/src/App.vue` - Removed ToolPreview import and step
- Progress bar updated from 5 steps to 4 steps

## Migration Notes

No breaking changes - this is purely a UI improvement. The backend API remains unchanged.
