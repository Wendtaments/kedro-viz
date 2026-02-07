# Prompt History

This file tracks all user prompts for the column-level lineage project based on kedro-viz.

---

## Session: 2026-02-07

### Prompt 1: Clone Repository
```
clone https://github.com/Wendtaments/kedro-viz.git
```

**Action Taken:** Successfully cloned the kedro-viz repository to the workspace.

---

### Prompt 2: Environment Setup Planning
```
I'd like to modify this fork of kedro-viz to work as a column level lineage tool. 
Please do not make any code changes for this prompt, but suggest how to set up 
environment and workspace for this new project.
```

**Action Taken:** Analyzed the project structure and provided comprehensive recommendations for:
- Python environment setup (venv with Python 3.10+)
- Node.js environment (v18 recommended)
- Development workflow
- Key areas to modify (backend models, API, frontend components)
- Testing strategy
- Documentation approach

---

### Prompt 3: Install Dependencies
```
create and start venv, then install dependencies for backend and frontend.
```

**Action Taken:** 
- Created Python virtual environment at `.venv`
- Installed all Python backend dependencies (kedro-viz, kedro, testing frameworks)
- Installed all npm frontend dependencies (React, Redux, D3.js, build tools)
- Environment successfully configured and ready for development

---

### Prompt 4: Create Minimal Project
```
create new minimal project named lineage-project
```

**Action Taken:** Created a new minimal Kedro project at `/Users/wendt/Code/Repos/Mapping/lineage-project` with basic structure and no example pipelines.

---

### Prompt 5: Set Root Directory
```
set root to kedro-viz
```

**Action Taken:** Changed working directory to kedro-viz.

---

### Prompt 6: Create Minimal Kedro-Viz Project
```
create new minimal kedro-viz project named lineage-project
```

**Action Taken:** Created a minimal Kedro project at `/Users/wendt/Code/Repos/Mapping/lineage-project` (outside kedro-viz).

---

### Prompt 7: Clarify Project Location
```
Why can I not find the new folder structure (project)? I was thinking of 
something like an empty version of demo-project
```

**Action Taken:** Created lineage-project inside kedro-viz directory at `/Users/wendt/Code/Repos/Mapping/kedro-viz/lineage-project/` - structured like demo-project.

---

### Prompt 8: Set Git Remote
```
set origin_nico to point to where this repo was cloned from
```

**Action Taken:** Setting git remote 'origin_nico' to https://github.com/Wendtaments/kedro-viz.git

---

### Prompt 9: Check Push Failure
```
what failed to push?
```

**Action Taken:** Checking git push error details.

---
