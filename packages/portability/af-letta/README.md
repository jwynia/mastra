# @mastra/portability-af-letta

Support for Letta's .af (Agent File) format in Mastra, enabling seamless agent portability between Python and TypeScript ecosystems.

## Overview

The Agent File (.af) format is an open standard introduced by [Letta](https://github.com/letta-ai/letta) (formerly MemGPT) for serializing AI agents into portable JSON files. This package provides:

- **Import**: Parse and validate .af files to create Mastra agents
- **Export**: Serialize Mastra agents to .af format
- **Type Safety**: Full TypeScript types and Zod schemas
- **Validation**: Comprehensive error messages for debugging

## Installation

```bash
npm install @mastra/portability-af-letta
# or
pnpm add @mastra/portability-af-letta
# or
yarn add @mastra/portability-af-letta
```

## Quick Start

### Parsing an Agent File

```typescript
import { parseAgentFile } from '@mastra/portability-af-letta';
import { readFileSync } from 'fs';

// Parse an .af file
const agentJson = readFileSync('./my-agent.af', 'utf-8');
const agentData = parseAgentFile(agentJson);

console.log(`Loaded agent: ${agentData.name}`);
console.log(`Tools: ${agentData.tools.map(t => t.name).join(', ')}`);
```

### Safe Parsing with Error Handling

```typescript
import { safeParseAgentFile } from '@mastra/portability-af-letta';

const result = safeParseAgentFile(agentJson);

if (result.success) {
  console.log(`Agent: ${result.data.name}`);
} else {
  console.error('Parse failed:', result.error.message);
  if (result.error.validationErrors) {
    result.error.validationErrors.forEach(err => {
      console.error(`  ${err.path}: ${err.message}`);
    });
  }
}
```

### Validating Agent Files

```typescript
import { isValidAgentFile, getValidationErrors } from '@mastra/portability-af-letta';

// Quick validation
if (isValidAgentFile(agentJson)) {
  console.log('Agent file is valid');
}

// Get detailed errors
const errors = getValidationErrors(agentJson);
if (errors) {
  errors.forEach(err => {
    console.error(`${err.path}: ${err.message}`);
  });
}
```

### Working with TypeScript Types

```typescript
import type { AfAgentSchema, AfTool, AfMessage } from '@mastra/portability-af-letta';

// Type-safe agent manipulation
function addTool(agent: AfAgentSchema, tool: AfTool): AfAgentSchema {
  return {
    ...agent,
    tools: [...agent.tools, tool],
    updated_at: new Date().toISOString(),
  };
}

// Type-safe message creation
const message: AfMessage = {
  id: crypto.randomUUID(),
  role: 'user',
  text: 'Hello, assistant!',
  timestamp: new Date().toISOString(),
};
```

### Using Zod Schemas Directly

```typescript
import { afAgentSchema, toolSchema } from '@mastra/portability-af-letta';

// Validate partial data
const toolResult = toolSchema.safeParse({
  name: 'calculator',
  description: 'Perform calculations',
  type: 'python',
  parameters: {
    type: 'object',
    properties: {
      expression: {
        type: 'string',
        description: 'Math expression to evaluate',
      },
    },
    required: ['expression'],
  },
  source_code: 'def calculate(expression: str): return eval(expression)',
});

if (toolResult.success) {
  console.log('Valid tool:', toolResult.data.name);
}
```

## API Reference

### Parser Functions

#### `parseAgentFile(jsonString, options?)`
Parse and validate an .af file from a JSON string.

- **Throws**: `AgentFileParseError` on invalid input
- **Options**:
  - `maxSize`: Maximum file size in bytes (default: 50MB)
  - `autoFix`: Apply automatic fixes for common issues (default: true)
  - `strict`: Strict validation mode (default: false)

#### `safeParseAgentFile(jsonString, options?)`
Parse an .af file with a result object (never throws).

- **Returns**: `{ success: true, data: AfAgentSchema } | { success: false, error: AgentFileParseError }`

#### `parseAgentFileObject(data, options?)`
Parse an already-parsed JSON object.

#### `isValidAgentFile(jsonString)`
Quick validation check.

- **Returns**: `boolean`

#### `getValidationErrors(jsonString)`
Get detailed validation errors.

- **Returns**: `Array<{ path: string, message: string }> | null`

#### `extractAgentMetadata(jsonString)`
Extract basic metadata without full validation.

- **Returns**: Partial agent metadata or null

### Schema Exports

All Zod schemas are exported for direct use:

- `afAgentSchema` - Complete agent file schema
- `llmConfigSchema` - Language model configuration
- `embeddingConfigSchema` - Embedding configuration
- `coreMemoryBlockSchema` - Core memory blocks
- `messageSchema` - Conversation messages
- `toolSchema` - Tool definitions
- `toolRuleSchema` - Tool usage rules
- `toolCallSchema` - Tool invocations
- `toolResultSchema` - Tool results
- `toolParametersSchema` - Tool parameter schemas

### Type Exports

All TypeScript interfaces are exported:

- `AfAgentSchema` - Main agent file structure
- `AfLLMConfig` - LLM configuration
- `AfEmbeddingConfig` - Embedding configuration
- `AfCoreMemoryBlock` - Core memory block
- `AfMessage` - Message with tool calls
- `AfTool` - Tool definition
- `AfToolRule` - Tool usage rule
- `AfToolCall` - Tool invocation
- `AfToolResult` - Tool execution result
- `AfToolParameters` - Tool parameter schema
- `AfParameterProperty` - Individual parameter

## Auto-Fix Features

The parser can automatically fix common issues:

1. **Missing timestamps**: Adds current time for `created_at` and `updated_at`
2. **Missing version**: Defaults to "0.1.0"
3. **Empty arrays**: Initializes `core_memory`, `messages`, and `tools` as empty arrays
4. **Message timestamps**: Generates reasonable timestamps for messages without them
5. **Tool parameters**: Ensures proper structure with `type: "object"` and `properties`

Disable auto-fix with `{ autoFix: false }` in parse options.

## Error Handling

The `AgentFileParseError` class provides detailed error information:

```typescript
try {
  const agent = parseAgentFile(json);
} catch (error) {
  if (error instanceof AgentFileParseError) {
    console.error('Parse error:', error.message);
    
    // Check for validation errors
    if (error.validationErrors) {
      error.validationErrors.forEach(err => {
        console.error(`  ${err.path}: ${err.message}`);
      });
    }
    
    // Access original error
    if (error.cause) {
      console.error('Caused by:', error.cause.message);
    }
  }
}
```

## Validation Rules

The parser enforces these validation rules:

1. **Required fields**: `agent_type`, `name`, `system`, `llm_config`, `version`, timestamps
2. **Tool source code**: Required for `python` and `javascript` tool types
3. **Message indices**: `in_context_message_indices` must reference valid message positions
4. **Tool rules**: Must reference existing tools
5. **Timestamps**: Must be in ISO 8601 format
6. **Parameter schemas**: Must follow JSON Schema specification

## Contributing

This package is part of the Mastra framework. See the main [CONTRIBUTING.md](https://github.com/mastra-ai/mastra/blob/main/CONTRIBUTING.md) for guidelines.

## License

MIT - See [LICENSE](https://github.com/mastra-ai/mastra/blob/main/LICENSE) for details.