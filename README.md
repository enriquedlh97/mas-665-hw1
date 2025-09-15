# Enrique Crew AI System

A multi-agent CrewAI system that represents Enrique as an AI Studio student, capable of scheduling meetings, answering questions, and managing calendar availability through Calendly integration.

## 🎯 Project Overview

This system implements a **Backend Crew AI Agent** with multiple specialized agents that work together to:

1. **Chat with users** and understand their intent
2. **Check Enrique's Calendly availability** for requested dates/ranges
3. **Book meetings** after collecting required information
4. **Answer questions** about Enrique's background and interests

## 🤖 Agents

### 1. Chat Agent (Coordinator)
- **Role**: First contact and conversation orchestrator
- **Goal**: Understand user intent and delegate appropriate tasks
- **Capabilities**: Intent detection, conversation flow management, task delegation

### 2. Availability Agent
- **Role**: Calendar availability specialist
- **Goal**: Check Enrique's Calendly for available time slots
- **Capabilities**: Date range queries, alternative suggestions, slot formatting

### 3. Scheduler Agent
- **Role**: Meeting booking specialist
- **Goal**: Book meetings and provide confirmation details
- **Capabilities**: Contact collection, booking processing, confirmation management

### 4. Persona Agent
- **Role**: Enrique's personal representative
- **Goal**: Answer questions about Enrique's background and interests
- **Capabilities**: Bio information, project details, availability policies

## 🛠️ Technical Architecture

### Backend Abstraction
- **Playwright MCP Integration**: Direct web automation for Calendly interaction using [Microsoft's official Playwright MCP server](https://github.com/microsoft/playwright-mcp)
- **Modular Design**: Easy to swap backends (Calendly API ↔ Playwright MCP)
- **Stable Data Contracts**: Consistent interfaces for slot and booking data
- **Self-Contained**: Includes Playwright MCP server as a git submodule for complete portability

### Key Features
- **Terminal Interface**: Clean CLI with special commands (`:help`, `:reset`, `:debug`)
- **Docker Environment**: Complete containerized setup with UV package management
- **Environment Configuration**: Flexible settings via environment variables
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git (for submodule support)
- OpenAI API key
- Calendly account with a public booking link

### 1. Clone and Setup
```bash
git clone <repository-url>
cd mas-665-hw1

# Complete initial setup (submodules + build)
make setup
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration:
# - OPENAI_API_KEY=your_key_here
# - CALENDLY_LINK=https://calendly.com/your-handle/30min
```

### 3. Start the System

#### 🚀 **Daily Usage (Recommended)**
```bash
# Complete workflow: Build + Start + Chat
make start-chat
```

#### ⚡ **Fast Daily Usage (After Initial Build)**
```bash
# Quick start: Start + Chat (no rebuild)
make quick-chat
```

#### 🔧 **Development Workflow**
```bash
# One-time setup (first time only)
make setup

# Daily usage (fast)
make quick-chat

# When you make code changes
make build
make quick-chat
```

#### 📋 **Step-by-Step Commands**
```bash
# Three-step process (if you prefer)
make build    # Build images
make start    # Start services in background
make chat     # Open chat interface
```

**Note**: `make setup` builds everything once. After that, `make quick-chat` is fast (~10 seconds)!

### 4. Interact with the System
```bash
# The terminal interface will start automatically
# Try these example interactions:

# Check availability
"I'd like to schedule a meeting with Enrique"

# Learn about Enrique
"Tell me about Enrique's background"

# Check specific availability
"Is Enrique available this Friday afternoon?"
```

## 📋 Usage Examples

### Booking a Meeting
```
You: I'd like to schedule a meeting with Enrique
Assistant: I understand you'd like to schedule a meeting with Enrique.
Do you have a specific date or time in mind, or would you like me to check his availability for this week?

You: This Friday afternoon
Assistant: Available time slots:
1. Friday, January 17 at 2:00 PM - 3:00 PM
2. Friday, January 17 at 3:30 PM - 4:30 PM
...

You: 1
Assistant: Great! I've noted your slot selection.
Now I need some information to complete the booking:
• Your full name
• Your email address
...

You: John Smith john@example.com
Assistant: Meeting Successfully Booked! 🎉
Details:
• Date: Friday, January 17, 2025
• Time: 2:00 PM - 3:00 PM
• Attendee: john@example.com
• Status: Booked
```

### Learning About Enrique
```
You: Tell me about Enrique's background
Assistant: Based on Enrique's information:

# About Enrique
Enrique is an AI Studio student passionate about building intelligent systems...

Would you like to schedule a meeting to learn more about Enrique's work and interests?
```

### Natural Exit
```
You: That's all for today, thanks!
Assistant: You're very welcome! It was great helping you today.

Goodbye! Have a great day!
👋 Exiting Enrique's Crew AI System...
```

Or even more subtle:
```
You: Ok that's everything I needed
Assistant: Perfect! I'm glad I could help you with everything you needed.

Goodbye! Have a great day!
👋 Exiting Enrique's Crew AI System...
```

## 🛠️ Available Commands

### Make Commands (Recommended)
```bash
make help        # Show all available commands
make setup       # Complete initial setup (submodules + build)
make start-chat  # Build + Start + Chat (complete workflow)
make quick-chat  # Start + Chat (fast daily usage)
make build       # Build Docker images (when code changes)
make start       # Start services in background
make chat        # Open chat interface (requires services running)
make stop        # Stop all services
make clean       # Clean up containers and images
make logs        # Show service logs
make test        # Run tests
```

### Workflow Comparison
| Command | Time | Use Case |
|---------|------|----------|
| `make setup` | ~3 minutes | First-time setup only |
| `make start-chat` | ~3 minutes | Complete workflow (build + start + chat) |
| `make quick-chat` | ~10 seconds | Daily usage (fast!) |
| `make build` | ~2 minutes | After code changes |
| `make chat` | Instant | When services already running |

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | Required |
| `CALENDLY_LINK` | Enrique's public Calendly link | Required |
| `MCP_SERVER_URL` | Playwright MCP server URL | `http://localhost:3000` |
| `TIMEZONE` | Timezone for scheduling | `America/New_York` |
| `BOOKING_BACKEND` | Backend to use | `playwright_mcp` |
| `DEBUG` | Enable debug mode | `false` |

### Special Commands
- `:help` - Show available commands
- `:reset` - Clear conversation state
- `:debug` - Show current conversation state
- `:quit` - Exit the application

### Natural Exit
The agent intelligently recognizes when you want to end the conversation. You can express this in many ways:
- "That's all for today, thanks"
- "Thanks, I'm good"
- "That's everything I needed"
- "Ok that's all thanks"
- "I'm done"
- "Goodbye"
- "See you later"

The agent uses natural language understanding to detect your intent to end the conversation, even if you don't explicitly say "exit" or "goodbye".

## 🏗️ Project Structure

```
/crew/
  agents/           # CrewAI agent definitions
    chat_agent.py
    availability_agent.py
    scheduler_agent.py
    persona_agent.py
  tasks/            # CrewAI task implementations
    check_availability.py
    book_meeting.py
    answer_persona.py
    orchestrate_conversation.py
  backends/          # Backend implementations
    base_backend.py
    playwright_mcp.py
  data/             # Static data
    persona.md
  config/           # Configuration
    settings.py
main.py             # Terminal interface
requirements.txt    # Dependencies
Dockerfile          # Container definition
docker-compose.yml  # Multi-service setup
Makefile           # Convenience commands
```

## 🧪 Testing

```bash
# Run tests
make test

# Run specific test file
docker-compose exec crewai-app python -m pytest tests/test_agents.py
```

## 🔄 Development

### Adding New Agents
1. Create agent in `crew/agents/`
2. Define agent creation function
3. Add to main interface
4. Update tests

### Adding New Backends
1. Implement `BaseBackend` interface
2. Add backend selection logic
3. Update environment configuration
4. Test with both backends

### Modifying Tasks
1. Update task in `crew/tasks/`
2. Modify agent assignments
3. Test task execution
4. Update documentation

## 🐛 Troubleshooting

### Common Issues

**MCP Server Connection Failed**
```bash
# Check if MCP server is running
curl http://localhost:3000/health

# Verify submodules are initialized
git submodule status

# Re-initialize submodules if needed
make setup

# Check Docker logs
docker-compose logs playwright-mcp
```

**OpenAI API Errors**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Docker Build Issues**
```bash
# Clean and rebuild
make clean
make build

# Or complete reset
make clean
make setup
```

**Slow Startup Issues**
```bash
# Make sure you're using the fast commands
make start-chat  # Fast (10 seconds)
# NOT: docker-compose up --build  # Slow (3+ minutes)

# If still slow, rebuild once
make build
make start-chat
```

## 📝 Assignment Requirements Checklist

- ✅ **Two or more agents** with clear roles, goals, and backstories
- ✅ **Two or more tasks** with descriptions and expected outputs
- ✅ **Crew formation** that orchestrates agents and tasks
- ✅ **Terminal interaction** to run the agent system
- ✅ **Clean, well-commented code** following Python best practices
- ✅ **Tool integration** (Playwright MCP for enhanced capabilities)

## 🎓 Learning Outcomes

This project demonstrates:

1. **Multi-Agent Systems**: How specialized agents collaborate
2. **Backend Abstraction**: Clean interfaces for different implementations
3. **Docker Orchestration**: Containerized multi-service applications
4. **Terminal Interfaces**: Interactive CLI design patterns
5. **Error Handling**: Graceful failure management
6. **Configuration Management**: Environment-based settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Enrique Diaz de Leon Hicks**
AI Studio Student
Building intelligent multi-agent systems
