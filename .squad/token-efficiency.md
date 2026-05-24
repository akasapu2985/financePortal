# Token Efficiency — Mandatory Agent Rule

Every agent on this team MUST follow these rules:

## Rules

1. **Minimal responses** — Lead with the answer. No filler, no restating the question.
2. **No context dumping** — Never paste large code blocks, file contents, or logs back into responses. Summarize.
3. **Use tracking, not memory** — Work state lives in GitHub Issues (source of truth) + session plan.md for coordination. Don't carry state in conversation.
4. **Don't re-read** — If a file was already read this session, don't read it again unless it changed.
5. **Lean prompts** — When spawning sub-agents, include ONLY what they need. No backstory, no full file contents they can read themselves.
6. **Clear between steps** — Use `/clear` after completing a work item before starting the next. Do this autonomously — never ask the user for permission to clear.
7. **Summarize, don't echo** — After reading a file or running a command, report the 1-2 key facts. Don't echo the output.

## Why

Token cost is real. Context windows fill fast. Older responses compound exponentially. A production team communicates lean.
