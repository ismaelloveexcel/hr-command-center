# REPO RULES (Do Not Modify)

These rules enforce simplicity, stability, and HR-first design.

## Build Principles
- Every feature must reduce HR workload or compliance risk. If not, it will not be built.
- The repository must remain easy to understand by HR, not only developers.

## Architecture Constraints
- One request system only.
- One HR dashboard only.
- No pass systems.
- No multiple dashboards.
- No gamification or analytics dashboards.
- No additional modules without being explicitly defined in roadmap.

## Code Constraints
- No file should exceed 400 lines.
- All code must be human-readable.
- No placeholders for future features.
- Only build features defined in the phases.

## Security & Compliance
- No credentials in repo.
- No personal data logged in plaintext.
- All HR lifecycle changes must be logged.
