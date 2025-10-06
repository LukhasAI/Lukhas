---
status: wip
type: documentation
---
# 🎯 ChatGPT MCP Connector - Minimal Format Implementation Success

**Date:** 2025-10-03T03:10:00Z
**Status:** ✅ READY FOR CHATGPT INTEGRATION

## 🚀 Implementation Summary

We have successfully implemented the **exact minimal format** specified by GPT Pro to resolve the "search action not found" error in ChatGPT MCP connectors.

### ✅ Key Achievements

1. **Minimal Schema Format**: Implemented GPT Pro's exact minimal tool schema specifications
2. **Compact Response Format**: Modified response structure to match ChatGPT requirements  
3. **Syntax Fix**: Resolved missing line break causing server crashes
4. **Verified Testing**: Both search and fetch tools working with proper minimal format

### 🛠️ Technical Implementation

#### Search Tool Minimal Format
```json
{
  "name": "search",
  "description": "Search over LUKHAS sources",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 5 }
    },
    "required": ["query"]
  }
}
```

**Response Format:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"hits\":[{\"title\":\"...\",\"snippet\":\"...\",\"url\":\"...\"}]}"
    }
  ]
}
```

#### Fetch Tool Minimal Format
```json
{
  "name": "fetch", 
  "description": "Fetch a document by URL",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "format": "uri" }
    },
    "required": ["url"]
  }
}
```

**Response Format:**
```json
{
  "content": [
    {
      "type": "text", 
      "text": "{\"title\":\"...\",\"url\":\"...\",\"mimeType\":\"...\",\"text\":\"...\"}"
    }
  ]
}
```

### 🧪 Testing Results

**Search Tool Test:**
```
Status: 200
✅ Minimal format detected - has 'hits' array
Response contains: {hits: [{title, snippet, url}, ...]}
```

**Fetch Tool Test:**
```
Status: 200  
✅ Minimal fetch format detected - has all required fields
Fields: ['title', 'url', 'mimeType', 'text']
```

**Ngrok Tunnel Test:**
```
✅ HTTPS tunnel active: https://207071460ff8.ngrok-free.app/mcp
✅ External access verified with minimal format response
✅ Search tool returns compact JSON: {hits: [...]}
```

### 🔧 Current Configuration

**MCP Server:**
- **File:** `mcp-streamable.mjs` 
- **Port:** 8766
- **Protocol:** MCP 2024-11-05
- **Transport:** Streamable HTTP (single endpoint)
- **Status:** ✅ Running with minimal format

**ngrok Tunnel:**
- **URL:** `https://207071460ff8.ngrok-free.app/mcp`
- **Status:** ✅ Active and verified
- **Security:** HTTPS enabled

**ChatGPT Connector:**
- **File:** `chatgpt-connector.json`
- **URL:** Updated to new ngrok tunnel
- **Status:** ✅ Ready for ChatGPT integration

### 🎯 Next Steps

1. **Add to ChatGPT:** Use the connector configuration with URL `https://207071460ff8.ngrok-free.app/mcp`
2. **Test Integration:** Verify that ChatGPT can now access search and fetch tools without "action not found" error
3. **Monitor Performance:** Check that minimal format provides the expected functionality

### 🔍 GPT Pro Compliance Verification

✅ **All 5 GPT Pro Tests Passing:**
1. Search tool schema matches minimal requirements
2. Fetch tool schema matches minimal requirements  
3. Response format is compact JSON inside MCP content
4. Required fields present in all responses
5. Permissive argument handling implemented

### 📋 Technical Notes

- **Syntax Issue Fixed:** Resolved missing line break between search and fetch cases
- **Server Stability:** Using nohup to prevent terminal interruption
- **Response Format:** JSON.stringify() used to create compact text content
- **Error Handling:** Graceful degradation with informative error messages

---

**The ChatGPT MCP connector is now ready with GPT Pro's exact minimal format specifications implemented.**