<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Integrating .af Agent Files into Mastra (TypeScript)

Modern AI products increasingly rely on **portable, state‐rich agent formats**. Letta’s open “Agent File” (.af) specification serialises an entire agent – prompts, memory, tools, configuration and history – into a single JSON package, while Mastra is quickly becoming the de-facto TypeScript framework for building agentic workflows. Adding first-class .af support to Mastra therefore unlocks three benefits:

* seamless agent exchange between Python-centric Letta and JS-centric Mastra
* reproducible hand-off from research notebooks to production apps
* one-click backups, versioning and diffing of Mastra agents for teams

Below is a pragmatic engineering guide that walks through architecture, data mapping, TypeScript implementation, and developer‐experience considerations.

## 1. Technical Overview

Porting the format requires four high-level capabilities:

1. **Validate** incoming .af files against the published schema.
2. **Transform** each .af component (memory blocks, tools, configs…) into Mastra equivalents.
3. **Instantiate** a Mastra `Agent` object with converted artefacts and optional memory storage.
4. **Serialise** an in-memory Mastra agent back to .af for export and version control.

![Architecture diagram for implementing .af agent file support in Mastra TypeScript framework](https://pplx-res.cloudinary.com/image/upload/v1751375875/pplx_code_interpreter/77507599_pkly44.jpg)

Architecture diagram for implementing .af agent file support in Mastra TypeScript framework

## 2. Schema Decomposition

An .af file is a single JSON document whose root object (`AgentSchema`) combines six logical sections:

* Core fields (id, name, system prompt, version)
* Configuration (LLM + embedding)
* Memory \& messages
* Tooling (schemas, code, rules)
* Metadata \& tags
* Timestamps

![Hierarchical view of .af AgentSchema structure](https://pplx-res.cloudinary.com/image/upload/v1751376021/pplx_code_interpreter/5e7c3962_kr4a59.jpg)

Hierarchical view of .af AgentSchema structure

### Why this matters

Mastra already exposes analogous constructs (`Agent`, `Memory`, tool definitions, model configs). Your adaptor therefore centres on **field mapping plus type-safe validation** rather than reinventing agent concepts.

## 3. Field-by-Field Mapping

The CSV below shows a direct mapping of every top-level .af field to its Mastra counterpart or conversion target.

Key observations:

* **System prompt → Agent.instructions**: pass straight through.
* **core_memory + messages → Memory store**: convert to Mastra’s `Memory` class (or a custom store implementing its interface).
* **tools**: transpile Python source into TypeScript (if possible) or embed as WASM-compatible micro-services; JSON schemas drop in unchanged.
* **tool_rules**: map simple rule types (max-count, child dependencies) into Mastra’s built-in workflow graph; complex conditional routing may require a bespoke “ToolRuleEngine”.


## 4. Implementation Plan

### 4.1 TypeScript packages to add

| Layer | Suggested package | Purpose |
| :-- | :-- | :-- |
| Schema validation | `zod` | Compile Pydantic-style JSON schema into Zod types for runtime and compile-time safety |
| .af parser | `@mastra/af-parser` (new) | Exposes `parseAf(json: string | object): ParsedAf` |
| Converters | `@mastra/af-converters` (new) | Functions `toMastraAgent(parsedAf)` and `fromMastraAgent(agent)` |
| CLI | `mastra-af` (new bin) | `mastra af import path.af` and `mastra af export <agentId>` |
| Tests | `vitest` | Snapshot tests on example .af bundles |

### 4.2 Parsing \& validation

```ts
// zod schema (excerpt)
const ParameterProps = z.object({
  type: z.string(),
  description: z.string().optional(),
});

const ToolSchema = z.object({
  name: z.string(),
  description: z.string(),
  parameters: z.object({
    type: z.literal('object').optional(),
    properties: z.record(ParameterProps),
    required: z.string().array().optional(),
  }),
  source_code: z.string().optional(),
  // ...
});

export const AfSchema = z.object({
  name: z.string(),
  system: z.string(),
  llm_config: z.record(z.any()),
  core_memory: z.array(z.any()),
  messages: z.array(z.any()),
  tools: z.array(ToolSchema),
  // remaining fields…
});
```


### 4.3 Conversion helpers

* `convertMemory(parsedAf)` → returns a `Memory` backed by `LibSQLStore` or in-memory.
* `convertTools(parsedAf)` → iterates tool list:
    * JSON schema stays JSON.
    * If `source_code` is Python and `tool_type === 'python'`, pipe through Transcrypt or prompt-based Codex transpiler; fallback to a remote execution service.
* `convertConfig(parsedAf.llm_config)` → builds `openai()` or other Mastra model provider.
* Assemble:

```ts
export function toMastraAgent(af: AfParsed): Agent {
  return new Agent({
    name: af.name,
    instructions: af.system,
    model: convertConfig(af.llm_config),
    tools: convertTools(af),
    memory: convertMemory(af),
  });
}
```


### 4.4 Export path

1. Walk Mastra `Agent` instance, serialise `Memory` threads and `Tool` metadata.
2. Add `created_at`, `updated_at`, `version`.
3. `JSON.stringify()` with canonical key ordering for clean diffs.
4. Optionally sign the file with SHA-256 for tamper detection.

## 5. Developer Experience

| Feature | Rationale | Implementation hint |
| :-- | :-- | :-- |
| **CLI import/export** | Mirrors `docker load/save`; easy for app builders | Reuse Mastra’s command scaffold (`create-mastra`) |
| **IDE autocomplete** | AfSchema→TypeScript types; prevents mismatched keys | `zod.infer<typeof AfSchema>` |
| **Playground visual diff** | Side-by-side JSON diff when saving | Use Monaco diff editor in Mastra UI |
| **Migration hooks** | When Af spec evolves, run codemod on load | Embed a `version` field and switch-case migrator |

## 6. Edge-Cases \& Mitigations

| Case | Risk | Mitigation |
| :-- | :-- | :-- |
| Missing `source_code` for tools | Tool not executable | Allow schema-only “webhook” tools and prompt LLM to supply call text |
| Non-deterministic `in_context_message_indices` | Out-of-bound indices crash load | Clamp indices to available messages; warn user |
| Secrets inside environment vars | Leak on Git commit | Strip or redact on export; provide `.env` sidecar |

## 7. Road-Map \& Effort Estimate

| Milestone | Duration | Owner |
| :-- | :-- | :-- |
| Zod schema + parser | 2 days | SDK team |
| Memory + tool converters (MVP, no code transpile) | 5 days | Core |
| CLI \& unit tests | 3 days | DX team |
| Round-trip export / import tested on sample .af files | 2 days | QA |
| Optional Python→TS transpilation PoC | 1 week | R\&D |

_Total core engineering: ~2.5 weeks._

## 8. Conclusion

Adding .af support to Mastra is **straightforward** because both ecosystems share the same conceptual building blocks. By validating with Zod, mapping fields one-to-one, and leaning on Mastra’s flexible memory and tool abstractions, you can let developers **drag-and-drop agents between Python and TypeScript stacks without rewriting logic or losing state**. The outlined modules, CLI commands and edge-case guards provide a production-ready blueprint you can iterate on as the Agent File standard evolves.

<div style="text-align: center">⁂</div>

[^1]: https://github.com/letta-ai/agent-file

[^2]: https://github.com/mastra-ai/mastra

[^3]: https://deepwiki.com/mastra-ai/apr3-workshop/3-agents\&rut=38e726606961d1c280c0b470b9581f380f2da348209ba459a200c32f08203517

[^4]: https://zenn.dev/aoyamadev/articles/07a627c5a45160

[^5]: https://www.ycombinator.com/companies/mastra

[^6]: https://zenn.dev/yosh1/articles/mastra-ai-agent-framework-guide

[^7]: https://maestra.ai

[^8]: https://mastra.ai

[^9]: https://dev.to/couchbase/building-multi-agent-workflows-using-mastra-ai-and-couchbase-198n

[^10]: https://workos.com/blog/mastra-ai-quick-start

[^11]: https://mastra.ai/en/reference/agents/agent

[^12]: https://mastra.ai/en/docs/agents/overview

[^13]: https://www.youtube.com/watch?v=nBLXpS6YoUk

[^14]: https://deepwiki.com/mastra-ai/repo-base/4.1-mastra-agent

[^15]: https://www.youtube.com/watch?v=bzkbf10MCjw

[^16]: https://apify.com/templates/ts-mastraai

[^17]: https://github.com/apify/actor-mastra-mcp-agent

[^18]: https://www.evnekquest.com/post/introducing-the-agent-file-af-a-standard-for-stateful-ai-agents

[^19]: https://www.evnekquest.com/post/agent-file

[^20]: https://learn.microsoft.com/en-us/answers/questions/1377273/does-azure-data-factory-support-json-schema-ref-fo

[^21]: https://www.reddit.com/r/AI_Agents/comments/1jr3wr6/agent_file_af_a_way_to_share_debug_and_version/

[^22]: https://news.ycombinator.com/item?id=43558617

[^23]: https://experienceleague.adobe.com/en/docs/experience-manager-65/content/forms/adaptive-forms-advanced-authoring/adaptive-form-json-schema-form-model

[^24]: https://www.linkedin.com/posts/alex-brooker-2280002_a-really-interesting-idea-here-unlocking-activity-7314950510808100865-PvxP

[^25]: https://docs.oracle.com/middleware/1213/core/RCUUG/rcu_schemas.htm

[^26]: https://ai.pydantic.dev/tools/

[^27]: https://www.youtube.com/watch?v=WzWJ8Kkn2kQ

[^28]: https://github.com/letta-ai/agent-file/blob/main/README.md

[^29]: https://openai.github.io/openai-agents-python/ref/function_schema/

[^30]: https://pypi.org/project/letta/

[^31]: https://www.linkedin.com/posts/micheletrevisiol_the-team-at-letta-is-launching-%F0%9D%97%94%F0%9D%97%B4%F0%9D%97%B2%F0%9D%97%BB%F0%9D%98%81-activity-7314968951829020672-0sao

[^32]: https://gist.github.com/sutyum/290adc26027cd5e7c5364de77288074c

[^33]: https://github.com/lando22/agents.json/tree/main

[^34]: https://www.linkedin.com/posts/abidyoussef_launching-agent-file-af-to-move-smart-activity-7317654552994799616-26-b

[^35]: https://github.com/letta-ai/letta/issues/2116

[^36]: https://github.com/jmilinovich/agents.json

[^37]: https://gist.github.com/tkersey/e4d9923922d80c065f9d

[^38]: https://cloud.google.com/dialogflow/cx/docs/reference/json-export

[^39]: https://ia.letaodescinq.com/agent-file-letta-ai-analyse/

[^40]: https://github.com/letta-ai/letta/blob/main/letta/serialize_schemas/pydantic_agent_schema.py

[^41]: https://stackoverflow.com/questions/74883956/pros-and-cons-of-pydantic-compared-to-json-schemas

[^42]: https://mastra.ai/en/docs/agents/agent-memory

[^43]: https://docs.pydantic.dev/latest/concepts/json_schema/

[^44]: https://github.com/drumnation/ts-import-move

[^45]: https://deepwiki.com/mastra-ai/mastra/3.1-memory-system

[^46]: https://www.reddit.com/r/typescript/comments/118fqtj/library_like_pydantic_but_for_typescript/

[^47]: https://www.elastic.co/docs/reference/apm/agents/nodejs/typescript

[^48]: https://github.com/mastra-ai/mastra/blob/main/docs/src/pages/docs/agents/01-agent-memory.mdx

[^49]: https://blog.logrocket.com/understanding-typescript-object-serialization/

[^50]: https://www.youtube.com/watch?v=zLlkfT6Od8A

[^51]: https://github.com/Aakanksha011/zod

[^52]: https://www.npmjs.com/package/@lewist9x%2Fbee-agent-framework

[^53]: https://support.zendesk.com/hc/en-us/articles/8357756553498-Importing-and-exporting-intents-for-advanced-AI-agents

[^54]: https://dev.to/emiroberti/zod-for-typescript-schema-validation-a-comprehensive-guide-4n9k

[^55]: https://github.com/i-am-bee/beeai-framework

[^56]: https://www.snaplogic.com/genai-app-builder-use-cases/import-export-customs-documentation-automation

[^57]: https://experienceleague.adobe.com/en/docs/core-services/interface/services/customer-attributes/crs-data-file

[^58]: https://stackoverflow.com/questions/76244674/how-can-i-import-a-simple-json-dataset-into-memgraph?rq=1

[^59]: https://experienceleague.adobe.com/en/docs/core-services/interface/services/customer-attributes/t-crs-usecase

[^60]: https://memgraph.com/docs/data-migration/json

[^61]: https://www.letta.com/blog/agent-file

[^62]: https://www.linkedin.com/posts/wooders_today-were-releasing-agent-file-af-an-activity-7313259398808682497-67lz

[^63]: https://www.reddit.com/r/LocalLLaMA/comments/197mnt5/whats_the_best_open_source_llm_for_returning_only/

[^64]: https://github.com/lastmile-ai/mcp-agent

[^65]: https://github.com/gm2552/memgpt-agent

[^66]: https://github.com/langchain-ai/openevals

[^67]: https://gist.github.com/mberman84/c95d69263d9c2ceb7d56cf336f13ae02?permalink_comment_id=4746545

[^68]: https://www.youtube.com/watch?v=4s_JQk2JSVI

[^69]: https://www.youtube.com/watch?v=QCdQe8CdWV0

[^70]: https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/retrieval-augmented-generation/retail_warranty_claim_chatbot.ipynb

[^71]: https://www.youtube.com/watch?v=OaB2stc6ThM

[^72]: https://github.com/openai/openai-cs-agents-demo

[^73]: https://github.com/letta-ai

[^74]: https://json-schema.org/learn/json-schema-examples

[^75]: https://github.com/letta-ai/letta

[^76]: https://json-schema.org/learn/miscellaneous-examples

[^77]: https://github.com/letta-ai/agent-file/blob/main/CITATION.cff

[^78]: https://github.com/cpacker/MemGPT/issues/261

[^79]: https://corporate.abercrombie.com/careers/home-offices/

[^80]: https://raw.githubusercontent.com/overturetool/documentation/master/documentation/VDM10LangMan/VDM10_lang_man.pdf

[^81]: https://en.wikipedia.org/wiki/RAW_(rolling_papers)

[^82]: https://raw.githubusercontent.com/cpacker/MemGPT/main/PRIVACY.md

[^83]: https://rawthentic.com/contact/

[^84]: https://raw.githubusercontent.com/gabrieleletta97/gabriele_letta.github.io/master/files/CV_Letta.pdf

[^85]: https://www.fanduel.careers/jobs/fanduel/customer-support-agent-evenings-and-weekends-2/

[^86]: https://blog.logrocket.com/schema-validation-typescript-zod/

[^87]: https://voltagent.dev

[^88]: https://dzone.com/articles/mastering-json-serialization-with-pydantic

[^89]: https://www.webdevtutor.net/blog/typescript-json-to-class-object

[^90]: https://www.tryfondo.com/blog/mastra-launches

[^91]: https://stackabuse.com/reading-and-writing-json-with-typescript/

[^92]: https://github.com/colinhacks/zod

[^93]: https://www.youtube.com/watch?v=IJYgMv1wH30

[^94]: https://github.com/mikaylaedwards/pydantic-model

[^95]: https://www.delftstack.com/howto/typescript/cast-a-json-object-to-a-class-in-typescript/

[^96]: https://www.youtube.com/watch?v=gtkGboGmD2M

[^97]: https://www.youtube.com/shorts/8iNgc1-PwMk

[^98]: https://www.reddit.com/r/javascript/comments/1kax5pz/mastraai_quickstart_how_to_build_a_typescript/

[^99]: https://dstest.info/Help_6.3/Schema/afCommandType_action.html

[^100]: https://lamatic.ai/docs/agents/json-agent

[^101]: https://github.com/letta-ai/letta/blob/main/letta/agent.py

[^102]: https://www.linkedin.com/posts/arun-kumar-phd-27288942_agents-letta-llm-activity-7313499481155457024-Gskl

[^103]: https://github.com/phillipdupuis/pydantic-to-typescript

[^104]: https://github.com/i-am-bee/beeai-framework/blob/main/typescript/examples/README.md

[^105]: https://raw.githubusercontent.com/jktfe/myaimemory-mcp/HEAD/README.md

[^106]: https://www.reddit.com/r/WorkOnline/comments/18yc44w/chat_customer_support_agent_is_it_a_stressful_and/

[^107]: https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/f98958908605d00d41f693f253df0b58/bd1f571f-1b67-4a76-ae1d-84333fa7e1dc/81749193.csv

