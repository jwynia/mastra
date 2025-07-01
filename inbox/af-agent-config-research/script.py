import json

# Create a schema mapping between .af format and Mastra agent structure
af_to_mastra_mapping = {
    "Component Mapping": {
        ".af Core Components": {
            "agent_type": "String identifier (e.g., 'memgpt')",
            "name": "Agent display name",
            "description": "Optional agent description",
            "system": "System prompt/instructions",
            "llm_config": "Model configuration (provider, model name, parameters)",
            "embedding_config": "Embedding model settings",
            "core_memory": "List of memory blocks (personality, user info)",
            "messages": "Complete message history with metadata",
            "in_context_message_indices": "Which messages are in current context",
            "tools": "Tool definitions (schema, source code, metadata)",
            "tool_rules": "Tool execution rules and constraints",
            "tool_exec_environment_variables": "Environment variables for tools",
            "tags": "Agent tags/labels",
            "metadata_": "Additional metadata",
            "version": "Schema version",
            "created_at": "Creation timestamp",
            "updated_at": "Last update timestamp"
        },
        "Mastra Agent Equivalent": {
            "name": "Agent.name",
            "description": "Agent.description", 
            "instructions": "Agent.instructions (from .af system field)",
            "model": "Agent.model (derived from llm_config)",
            "tools": "Agent.tools (converted from .af tools)",
            "memory": "Agent.memory (converted from core_memory + messages)",
            "workflows": "Not directly supported in .af",
            "evals": "Not directly supported in .af",
            "voice": "Not directly supported in .af"
        }
    },
    "Key Differences": {
        "Memory Management": {
            "af_approach": "Explicit core_memory blocks + message history",
            "mastra_approach": "Memory class with storage adapters"
        },
        "Tool Definitions": {
            "af_approach": "Complete tool source code + JSON schema",
            "mastra_approach": "TypeScript functions with type definitions"
        },
        "Context Management": {
            "af_approach": "in_context_message_indices array",
            "mastra_approach": "Handled by memory system automatically"
        }
    }
}

# Write to CSV for reference
import pandas as pd

# Flatten the mapping for CSV output
rows = []
for category, items in af_to_mastra_mapping.items():
    if isinstance(items, dict):
        for subcategory, details in items.items():
            if isinstance(details, dict):
                for key, value in details.items():
                    rows.append({
                        "Category": category,
                        "Subcategory": subcategory,
                        "Field": key,
                        "Description": value
                    })
            else:
                rows.append({
                    "Category": category,
                    "Subcategory": subcategory,
                    "Field": "",
                    "Description": details
                })

df = pd.DataFrame(rows)
df.to_csv("af_mastra_mapping.csv", index=False)

print("Component mapping analysis complete:")
print(f"Total mappable components: {len([r for r in rows if r['Category'] == 'Component Mapping'])}")
print(f"Key differences identified: {len([r for r in rows if r['Category'] == 'Key Differences'])}")
print("\nCSV file 'af_mastra_mapping.csv' created with detailed mapping")