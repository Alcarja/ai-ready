# Setting Up Google Generative AI Agents with RAG

This guide explains how to set up Google Gemini agents to use your Retrieval-Augmented Generation (RAG) system with the vector store we created.

## Overview

Google's Generative AI agents can use **function calling** (also called tool use) to interact with external systems. In your case, the agent will:
1. Receive a user question through the `/ask` route
2. Call a RAG function to search your vector database
3. Use the retrieved context to generate an accurate answer

## Architecture

```
User Question (/ask endpoint)
    ↓
Agent receives question
    ↓
Agent calls RAG search function (via tool use)
    ↓
RAG function:
  - Vectorizes the question
  - Searches Chroma database
  - Returns top relevant chunks
    ↓
Agent synthesizes answer using context
    ↓
Return to user
```

## Step-by-Step Implementation

### Step 1: Understand Google Generative AI Function Calling

Google's `genai` library supports function calling, which allows the model to request to call specific functions you define. The flow is:
- Define available functions/tools with descriptions and parameters
- Send the function definitions to the API along with the user question
- The model decides which functions to call and with what parameters
- You execute those functions and send results back to the model
- The model generates the final response

### Step 2: Create a RAG Search Function

You already have `search_similar_chunks()` in `app/services/vector_store.py`. This function needs to be callable from the agent, so consider:

1. **Wrap the RAG logic** - Create a new function (e.g., `search_documents()`) that:
   - Takes a user question as input
   - Calls `generate_embeddings()` on the question
   - Calls `search_similar_chunks()` with the query embedding
   - Formats the results as a readable string

2. **Format output** - The function should return a string containing:
   - The most relevant document chunks
   - Their relevance scores (distances)
   - Page/chunk information for reference

### Step 3: Define Function Schema for the Agent

The agent needs to know about your RAG search function. Create a function definition that includes:

1. **Function metadata**:
   - `name`: A short identifier (e.g., "search_documents")
   - `description`: What the function does (e.g., "Search the document database for information relevant to a user query")

2. **Parameters schema** (describe what inputs the function needs):
   - `type`: Should be "object"
   - `properties`:
     - `query`: A string parameter for the user's search query
     - Add descriptions for each parameter
   - `required`: List which parameters are required

Example structure (in JSON/dict format):
```
{
  "name": "search_documents",
  "description": "Search company documents for relevant information",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query to find relevant documents"
      }
    },
    "required": ["query"]
  }
}
```

### Step 4: Create the Agent Controller

Create a new file (e.g., `app/controllers/ragAgentController.py`) that implements:

1. **Define available tools** - List the function schema(s) your agent can use (just your RAG search function for now)

2. **Create the agent function** that:
   - Takes a user question as input
   - Initializes the Gemini model with `genai.GenerativeModel()`
   - Defines the tools/functions the model can call
   - Sends the question to the model with the tool definitions
   - Processes the model's response:
     - If the model wants to call a tool, execute that tool
     - Send the tool results back to the model
     - Continue until the model provides a final text response

3. **Implement tool execution**:
   - Check what function the model wants to call
   - Extract the parameters from the model's request
   - Call your `search_documents()` function with those parameters
   - Format the results

4. **Handle the response loop**:
   - The model might need to call the tool multiple times
   - Keep calling until you get a `text` response (not a tool call)
   - Return the final text answer

### Step 5: Integrate with the /ask Route

Modify `app/routes/llmRoutes.py`:

1. **Create a new route** (e.g., `/ask/with-rag`) that:
   - Takes the user question
   - Calls your new RAG agent controller function
   - Returns the result

2. **Update the schema** if needed:
   - Keep the existing `AskRequest` schema
   - The response is still `AskResponse` (just the answer string)

Alternative: You could modify the existing `/ask` endpoint to automatically use RAG if available, but creating a new route makes it clearer.

### Step 6: System Prompt Design

Your agent needs good context about what it's doing. Create a system prompt that:

1. **Identifies the agent's role** - "You are a helpful assistant that answers questions about company policies using our internal document database"

2. **Instructs how to use tools** - "When a user asks a question, search our documents first, then answer based on what you find"

3. **Sets behavior guidelines** - "If documents don't contain the answer, say so instead of guessing"

4. **Specifies answer format** - "Include the source/chunk reference when citing information"

You can pass this as the `system_instruction` parameter to `GenerativeModel()`.

### Step 7: Error Handling

Consider error cases:

1. **Empty search results** - What if no relevant documents are found?
   - Agent should recognize this and inform the user
   - You might want to fall back to general knowledge

2. **API failures** - What if the embedding API times out?
   - Catch exceptions and return appropriate error messages

3. **Invalid tool calls** - What if the model calls a tool with wrong parameters?
   - Validate parameters before executing
   - Send error message back to model to retry

### Step 8: Testing

Before deploying:

1. **Test with simple questions** - Ask questions about content you know is in your PDFs

2. **Test with out-of-scope questions** - Ask about topics not in your documents to see how the agent handles it

3. **Check tool calling** - Verify the agent is actually calling the search function (you can add logging)

4. **Verify answer quality** - Make sure answers cite the retrieved documents

## Key Considerations

### Model Choice
- Use `"gemini-1.5-flash"` for cost-effective operation with function calling
- Use `"gemini-1.5-pro"` if you need higher reasoning quality

### Temperature and Other Parameters
- Set `temperature=0.7` for balanced creativity and consistency
- Lower temperature (0.3-0.5) for more factual answers
- Higher temperature (0.8+) for more creative responses

### Tool Calling Behavior
- The model might not always call your tool - ensure your system prompt encourages it
- You can specify `tool_choice` to force the model to use tools if needed
- Check the response type to determine if a tool was called

### Performance Optimization
- The RAG search is fast (Chroma lookup), but vectorizing the query adds latency
- Consider caching frequently asked questions
- Monitor API usage and costs

## Summary of Files to Create/Modify

1. **New file**: `app/services/rag_agent_service.py` - Wraps RAG search into a callable function
2. **New file**: `app/controllers/ragAgentController.py` - Implements the agent logic with tool calling
3. **Modify**: `app/routes/llmRoutes.py` - Add new endpoint or integrate into existing one
4. **Documentation**: This file explains the approach

## Next Steps After Implementation

1. Add more tools - You could add functions to upload new PDFs, get summary statistics, etc.
2. Implement memory - Store conversation history for multi-turn interactions
3. Add prompt templates - Improve answer formatting with structured prompts
4. Create admin endpoints - Allow adding/removing documents from the vector store
5. Analytics - Track which questions users ask and which documents they find most relevant
