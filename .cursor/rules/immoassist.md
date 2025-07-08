# ImmoAssist Project Rules

## Code Style and Standards

### Language and Communication

- Always respond in Russian when user asks in Russian
- Use professional and technical language
- Avoid emojis in code and documentation
- Write clear, concise comments in English

### Code Quality Standards

- Follow PEP 8 with 88 character line length
- Use type hints consistently
- Write docstrings for all public functions and classes
- Use Google-style docstring format
- Follow SOLID principles in architecture

### Project Structure

- Maintain clean separation of concerns
- Use dataclasses for configuration
- Implement proper error handling with custom exceptions
- Use Pydantic models for data validation
- Follow enterprise-grade patterns

### AI Agent Development

- Implement multi-agent architecture with clear responsibilities
- Use Google ADK patterns and best practices
- Ensure proper tool delegation and coordination
- Maintain conversation context and state management
- Implement structured logging for debugging

### Testing and Quality Assurance

- Write unit tests for critical components
- Use pytest for testing framework
- Implement integration tests for agent workflows
- Maintain high code coverage
- Use pre-commit hooks for quality checks

### Documentation

- Keep README.md comprehensive and up-to-date
- Document all major components and their purposes
- Include architecture diagrams and flow charts
- Provide clear setup and installation instructions
- Document API endpoints and data models

### Security and Best Practices

- Never hardcode sensitive information
- Use environment variables for configuration
- Implement proper authentication and authorization
- Follow secure coding practices
- Validate all user inputs

### Performance and Scalability

- Optimize for production deployment
- Implement proper caching strategies
- Use async/await for I/O operations
- Monitor performance metrics
- Plan for horizontal scaling

### Git and Version Control

- Write descriptive commit messages in English
- Use conventional commit format
- Keep commits focused and atomic
- Maintain clean git history
- Use feature branches for development

### External Integrations

- Implement proper error handling for external APIs
- Use retry mechanisms for transient failures
- Validate external API responses
- Implement rate limiting where necessary
- Monitor external service health

### Multi-language Support

- Support German, English, and Russian languages
- Implement proper language detection
- Maintain consistent terminology across languages
- Use proper localization patterns
- Handle special characters and encoding correctly
