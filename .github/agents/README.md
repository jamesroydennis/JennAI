# JennAI Coding Agents

This directory contains custom GitHub Copilot agent configurations for the JennAI project.

## Available Agents

### Peter - The Coding Agent

**File**: `peter.md`

Peter is your primary coding agent specialized in the JennAI codebase. Use Peter when you need help with:

- Writing Python code for JennAI
- Implementing Flask web application features
- Working with AI services and business logic
- Writing tests and maintaining code quality
- Understanding the JennAI architecture and project structure

**To use Peter:**

In GitHub Copilot Chat, you can invoke Peter using:
```
@peter help me implement a new feature for...
```

Or through the GitHub UI when creating issues or pull requests, you can mention Peter to get specialized coding assistance.

## How Custom Agents Work

Custom agents are markdown files that provide specialized instructions to GitHub Copilot. Each agent has:

1. **Role Definition**: What the agent specializes in
2. **Expertise**: Technical skills and domain knowledge
3. **Instructions**: How the agent should approach tasks
4. **Personality**: The agent's communication style and approach

## Adding New Agents

To add a new custom agent:

1. Create a new `.md` file in this directory
2. Define the agent's role, expertise, and instructions
3. Name the file descriptively (e.g., `database-expert.md`, `frontend-specialist.md`)
4. Update this README to document the new agent

## Learn More

For more information about GitHub Copilot custom agents, see:
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Custom Instructions for Copilot](https://docs.github.com/en/copilot/customizing-copilot)
