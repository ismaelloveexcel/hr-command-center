# REPO RULES (Do Not Modify)
These rules enforce simplicity, control and HR-first design.

## Build Principles
- Every feature must reduce HR workload or compliance risk.
- All code must be understandable by HR.

## Architecture Constraints
- One unified request system only.
- One HR dashboard only.
- No pass systems.
- No extra dashboards.
- No analytics dashboards or charts.
- No additional modules not explicitly defined.

## Code Constraints
- No file > 400 lines.
- No placeholders for future ideas.
- No dead code.
- No generated stubs unless currently needed.

## Security
- No personal data in logs.
- No credentials in repo.
