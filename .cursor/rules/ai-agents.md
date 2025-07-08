# AI Agent Development Rules

## Agent Architecture

### Multi-Agent System Design

- Each agent should have a single, well-defined responsibility
- Implement clear delegation patterns between agents
- Use coordinator pattern for complex workflows
- Maintain agent independence and loose coupling
- Implement proper error propagation between agents

### Agent Communication

- Use structured message formats for inter-agent communication
- Implement proper context passing between agents
- Maintain conversation state across agent interactions
- Use tool-based communication for complex operations
- Implement proper error handling for agent failures

### Tool Integration

- Each tool should have a clear, single purpose
- Implement proper input validation for all tools
- Use Pydantic models for tool input/output validation
- Implement proper error handling and recovery
- Document tool behavior and limitations

## Google ADK Best Practices

### Agent Definition

- Use descriptive agent names and descriptions
- Implement clear instruction sets for each agent
- Use proper model selection for different agent types
- Implement proper tool assignment and delegation
- Follow ADK patterns for agent configuration

### Tool Implementation

- Use FunctionTool decorator for all tools
- Implement proper type hints for all tool parameters
- Use structured output schemas for tool responses
- Implement proper error handling within tools
- Follow ADK tool naming conventions

### Configuration Management

- Use centralized configuration for all agents
- Implement environment-specific settings
- Use feature flags for optional functionality
- Implement proper validation for configuration
- Use secure storage for sensitive configuration

## Conversation Management

### Context Handling

- Maintain conversation context across interactions
- Implement proper session management
- Use structured data for context storage
- Implement context cleanup and expiration
- Handle context overflow and truncation

### User Experience

- Provide clear, actionable responses
- Implement proper error messages and recovery
- Use consistent language and terminology
- Implement proper multi-language support
- Provide helpful suggestions and guidance

### Response Generation

- Use structured response formats
- Implement proper source attribution
- Provide context-aware responses
- Use appropriate response length and detail
- Implement proper formatting and presentation

## Quality Assurance

### Testing Strategies

- Write unit tests for individual agents
- Implement integration tests for agent workflows
- Test conversation flows and context handling
- Implement performance testing for agent responses
- Test error handling and recovery scenarios

### Monitoring and Logging

- Implement structured logging for all agent interactions
- Monitor agent performance and response times
- Track conversation quality and user satisfaction
- Implement proper error tracking and alerting
- Monitor external API usage and costs

### Security Considerations

- Implement proper input sanitization
- Use secure communication channels
- Implement proper authentication and authorization
- Monitor for potential security vulnerabilities
- Follow secure coding practices for AI systems
