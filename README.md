# exprule - Experience Rule Engine for AI Agents

A pure Python, lightweight experience rule engine that enables AI agents to learn from experience, share knowledge, and improve over time.

## Features

- **Three-layer Experience Structure**: Task → Step → Action hierarchy
- **Multiple Storage Backends**: In-memory, SQLite (with optional Neo4j support)
- **Context-aware Querying**: Find relevant experiences based on current context
- **Q-learning Weight Updates**: Automatic weight adjustment based on success/failure feedback
- **Simple Agent Integration**: Easy API for query_experience(), record_experience(), update_feedback()
- **Serialization & Versioning**: Import/export experiences, track versions
- **Zero External Dependencies**: Core only requires pydantic and networkx

## Installation

```bash
pip install exprule
```

Or with optional dependencies:

```bash
pip install "exprule[neo4j,redis,yaml]"
```

## Quick Start

```python
from exprule import BaseAgentAdapter

# Create an agent adapter
agent = BaseAgentAdapter(agent_id="my_agent")

# Create and record an experience
exp = agent.create_simple_experience(
    task_name="Hello World",
    description="A simple hello world task",
    goal="Print hello world",
    tags=["hello", "example"],
    domain="examples"
)
agent.record_experience(exp)

# Query for experience
result = agent.query_experience("hello")

# Update feedback on success/failure
if result:
    agent.update_feedback(result.experience_id, success=True)
```

## Core Concepts

### Experience Structure

```
Experience
  └── Task (macro-level)
       ├── goal, success_criteria
       ├── tags, domain, weight, usage_count
       └── Steps (middle-level)
            ├── order, preconditions, postconditions
            └── Actions (micro-level)
                 ├── tool_name, input_params, output_result
```

### Storage Backends

```python
from exprule.storage.memory import MemoryStorage
from exprule.storage.sqlite import SQLiteStorage

# In-memory storage (default)
storage = MemoryStorage()

# SQLite persistent storage
storage = SQLiteStorage("experiences.db")
```

### Querying & Updating

```python
from exprule import QueryEngine, UpdateEngine, Context

query_engine = QueryEngine(storage)
update_engine = UpdateEngine(storage)

# Context-aware query
ctx = Context(
    context_id="ctx1",
    tags=["coding", "python"],
    user_id="user123"
)
results = query_engine.query("python", context=ctx)

# Record success/failure
update_engine.record_success(experience_id="exp1")
```

## Examples

See the `/examples` directory for complete usage examples.

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
```

## License

MIT License
