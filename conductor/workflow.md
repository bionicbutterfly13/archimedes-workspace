# Conductor Workflow

## Branch Protocol

1. **Feature branches**: `feature/{NNN}-{name}` from master
2. **Work on branch**: All commits on feature branch
3. **Merge when complete**: Squash or merge to master
4. **Delete branch**: After merge

## Track Lifecycle

1. **Create track**: `conductor/tracks/{NNN}-{name}/`
2. **Write spec.md**: Requirements, constraints, success criteria
3. **Write plan.md**: Phased tasks with IO map
4. **Execute**: Work through tasks, mark `[~]` then `[x]`
5. **Complete**: All tasks done, merge, journal entry

## Task Markers

```markdown
- [ ] Pending (unclaimed)
- [~] In progress (claimed)
- [x] Complete [commit-sha]
```

## Commit Format

```
<type>(<scope>): <description>

<body>

AUTHOR Mani Saint-Victor, MD
```

Types: feat, fix, refactor, docs, test, chore

## Quality Gates

Before marking task complete:
- Code works as expected
- No regressions
- Documentation updated if needed

## When Conductor is Required

- New feature (3+ files)
- Architectural changes
- API additions
- Integration work

## When Conductor is Optional

- Bug fixes (single file)
- Documentation updates
- Test additions
- Small refactors
