# Talk API Endpoint Documentation

## Overview

The `/talk` endpoint provides a conversational AI interface for program-to-program communication, designed to facilitate natural language conversations between different applications with role-based personalities.

## Base URL

```
POST /api/talk
```

## Request Format

### JSON Body

```json
{
  "sender": "A",
  "receiver": "B", 
  "message": "Your message here",
  "session_id": "optional-session-123"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sender` | string | Yes | Role identifier for the sender (1-50 characters) |
| `receiver` | string | Yes | Role identifier for the receiver (1-50 characters) |
| `message` | string | Yes | The message to send (1-2000 characters) |
| `session_id` | string | No | Optional session identifier for conversation continuity (max 100 characters) |

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Response generated successfully",
  "data": {
    "reply": "Generated response message",
    "session_id": "session-123"
  }
}
```

### Error Response (400 Bad Request)

```json
{
  "success": false,
  "message": "Validation error",
  "data": {
    "errors": {
      "field_name": ["Error message"]
    }
  }
}
```

## Default Roles

### Role A: User
- **Name**: User
- **Personality**: Helpful and curious user asking questions about travel and tourism in Thailand
- **Style**: Casual, friendly, inquisitive

### Role B: Assistant
- **Name**: Assistant
- **Personality**: Knowledgeable Thai tourism assistant providing helpful, accurate, and enthusiastic recommendations
- **Style**: Helpful, informative, polite, enthusiastic about Thailand

## Additional Endpoints

### Get Session Information
```
GET /api/talk/session/{session_id}
```

Returns information about a conversation session including message count and existence status.

### Clear Session
```
DELETE /api/talk/session/{session_id}
```

Clears all conversation history for the specified session.

### Get Available Roles
```
GET /api/talk/roles
```

Returns the available role configurations with their personalities and styles.

## Example Usage

### Basic Conversation

```bash
curl -X POST http://localhost:5000/api/talk \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "A",
    "receiver": "B", 
    "message": "Hello! Can you recommend some attractions in Bangkok?"
  }'
```

### Session-based Conversation

```bash
# First message
curl -X POST http://localhost:5000/api/talk \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "A",
    "receiver": "B",
    "message": "Tell me about Thai food",
    "session_id": "my-session-123"
  }'

# Follow-up message in same session
curl -X POST http://localhost:5000/api/talk \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "A", 
    "receiver": "B",
    "message": "What about desserts?",
    "session_id": "my-session-123"
  }'
```

## Configuration

The Talk service can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | OpenAI API key for LLM integration |
| `OPENAI_API_BASE` | `https://api.openai.com/v1` | OpenAI API base URL |
| `TALK_MODEL` | `gpt-3.5-turbo` | Model to use for responses |
| `TALK_MAX_TOKENS` | `500` | Maximum tokens in response |
| `TALK_TEMPERATURE` | `0.7` | Response creativity (0.0-1.0) |
| `TALK_MAX_CONTEXT_LENGTH` | `10` | Maximum conversation turns to remember |

## Fallback Mode

If no OpenAI API key is provided, the service operates in fallback mode using rule-based responses. This ensures the endpoint remains functional even without LLM access.

## Features

- ✅ Role-based conversational AI
- ✅ Session management for conversation continuity  
- ✅ Configurable LLM integration (OpenAI compatible)
- ✅ Intelligent fallback responses
- ✅ Input validation and error handling
- ✅ Context-aware conversations
- ✅ Multi-language support (Thai/English)
- ✅ Token/context limits for performance optimization
- ✅ RESTful API design
- ✅ Comprehensive test coverage

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 404 | Session not found (for session endpoints) |
| 500 | Internal server error |