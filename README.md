## Current Implementation & Future Improvements

### Local AI Model Integration

Currently implementing a local AI model directly within the main app hosted in server/ for initial development and testing.

#### Planned: Separate AI Service Architecture

In the future, the AI model will be moved to a dedicated server and communicate with the main app through APIs. This architectural change will provide:

- **Enhanced Scalability**: AI model service can be scaled independently based on demand
- **Improved Reliability**: Failures in the AI model won't affect the main application, and vice versa
- **Better Resource Management**: AI processing can be optimized on specialized hardware
- **Service Independence**: AI model updates and maintenance won't require app downtime

### Any to Any App

The model we are using is an any-to-any model. For now we only enable text-to-text functionality in the frontend. In the future we will enable full any-to-any functionality in the frontend,

### Add "session_user" table and model

Use session users to enable storing chat history and continous chat.

### Add real user auth system

Add pages for user reigister and login. For now use Dummy user with id 1.

### Sliding window + Running summary

Currently using eager loading to load a conversation + all of its messages. This will have performance problem when the number of messages of a conversation is large.

For accelerating the processing, we should not query and send too many messages to the AI model all at once:

- Keep only the last N messages verbatim (e.g., 12–30 turns).
- Maintain a running summary of older content (update it whenever the convo exceeds a threshold).
  - After inserting a new message, check a cheap condition (e.g., msg_count_since_last_summary >= 30)
  - If tripped, enqueue a small incremental summarization over the range (last_summarized_message_id+1 … newest_safe_id).
- Prompt = system + running_summary + last_N_messages (+ optional facts/memories).
- Store the summary in your DB (you already have a conversation_summaries table above).

### Add test cases for endpoint chat_with_model

#### Test File Location

Place your test files in a dedicated tests directory at the project root or inside the server folder:
For endpoint tests, use a file like:

#### Integration Tests

These should test the endpoint as a whole, including FastAPI routing, dependency injection, and model interaction.

test cases:

- Successful chat request returns a valid response (mock model if needed)
- Request when model/tokenizer is not loaded returns 500 error
- Request with invalid payload returns 422 error (validation)
- Large input or edge-case input (e.g., empty message list)
- Response formatting (e.g., Markdown, newlines)

#### Unit Tests

These should test the logic inside the handler function, isolated from FastAPI and external dependencies.

Unit test cases:

- apply_chat_template produces expected output for a given conversation
- decode returns expected text for given token IDs
- Error handling: function raises HTTPException when model/tokenizer is None
- Output post-processing (e.g., stripping newlines, handling special tokens)

### Testing Strategy

- Use FastAPI’s TestClient for integration tests to simulate HTTP requests.
- Use mocking (e.g., unittest.mock) for unit tests to isolate dependencies like the model and tokenizer.
- Consider using fixtures to set up test data and mock objects.
