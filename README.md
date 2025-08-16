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
