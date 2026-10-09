Training material. Invented data.

# privacy-agent

This folder holds the GDPR request intake agent of cycle 6. The agent is NOT written yet:
participants write it during the training with the Claude Agent SDK (Python, in all three
starter repositories).

What is here:

- `policy.md`: the GDPR intake policy of Stejar Bank that the agent must follow.
- `requests/`: 8 synthetic GDPR requests (JSON, each with `"synthetic": true`).
- `requirements.txt`: the Python dependency of the agent (`claude-agent-sdk`).
- `output/`: where the agent writes its triage results and its audit log.

Install: nothing to do. The setup script of the repository installs `claude-agent-sdk` in the
`.venv` of the project (the `dev` extra of `pyproject.toml`). Do not create another environment.

Rules for the agent (from `policy.md`): it classifies and routes requests, it never sends a
reply to a requester, and it never reads customer data without human approval.
