# Git + GitHub Setup

## Initialize local Git
```bash
git init
git branch -M main
git add .
git commit -m "chore: initialize CI repair hackathon project"
```

## GitHub CLI route
Authenticate once:
```bash
gh auth login
```
Create and push:
```bash
gh repo create ci-repair-agent --public --source=. --remote=origin --push --description "Agentic CI Failure Investigator & Verified Repair System"
```
Use `--private` instead while developing if you prefer; follow organizer access requirements before judging.

## Browser route
Create an empty GitHub repo named `ci-repair-agent` without README/.gitignore/license, then:
```bash
git remote add origin https://github.com/<YOUR_USERNAME>/ci-repair-agent.git
git push -u origin main
```

## Verify
```bash
git remote -v
git status
```

## Suggested next branch
```bash
git checkout -b feat/evaluation-harness
```
