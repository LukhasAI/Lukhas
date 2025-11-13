# Pull Request

## Description
<!-- Provide a clear and concise description of what this PR does and why it's needed -->


### Type of Change
<!-- Check all that apply -->
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (code restructuring without changing external behavior)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Security enhancement
- [ ] Configuration change
- [ ] Dependency update

## Changes
<!-- List the key changes in this PR -->
-
-
-

## Testing Checklist
- [ ] **Unit tests**: New/updated unit tests added and passing
- [ ] **Integration tests**: Integration tests added/updated and passing
- [ ] **Smoke tests**: `make smoke` passes successfully
- [ ] **Manual testing**: Manually verified the changes work as expected
- [ ] **Test coverage**: No decrease in test coverage (or justified)
- [ ] **All tests pass**: `pytest -q` completes successfully
- [ ] **Edge cases**: Tested boundary conditions and error cases

## Security Checklist
- [ ] **No vulnerabilities**: Code scanned for security vulnerabilities
- [ ] **No secrets**: No API keys, passwords, or sensitive data committed
- [ ] **Guardian compliance**: Changes comply with Guardian safety protocols
- [ ] **Input validation**: User inputs are properly validated and sanitized
- [ ] **Authentication**: Authentication/authorization checks are in place where needed
- [ ] **Dependencies**: No known vulnerabilities in new/updated dependencies

## Code Quality Checklist
- [ ] **Linting**: Code passes linting checks (`make lint` or equivalent)
- [ ] **Type hints**: Functions have proper type annotations
- [ ] **Docstrings**: Public functions/classes have docstrings
- [ ] **F821 errors**: No undefined name errors (unused imports removed)
- [ ] **E402 errors**: No module level import errors (imports at top of file)
- [ ] **Code style**: Follows project coding standards and conventions
- [ ] **No debugging code**: No print statements, debugger calls, or commented-out code
- [ ] **Error handling**: Appropriate error handling and logging in place

## Documentation Checklist
- [ ] **README**: README.md updated if user-facing changes
- [ ] **Architecture docs**: Architecture documentation updated if design changes
- [ ] **API documentation**: API docs updated for endpoint/interface changes
- [ ] **Runbooks**: Runbooks updated for operational changes
- [ ] **CHANGELOG**: CHANGELOG.md updated with user-visible changes
- [ ] **Code comments**: Complex logic has explanatory comments
- [ ] **Migration guide**: Breaking changes documented with migration instructions

## References
<!-- Link related issues, PRs, documentation, and design docs -->

### Related Issues
<!-- Example: Fixes #123, Closes #456, Related to #789 -->


### Related PRs
<!-- Example: Depends on #100, Blocks #200 -->


### Documentation
<!-- Link to runbooks, design docs, architecture diagrams, etc. -->


## Deployment Notes
<!-- Describe any deployment considerations, configuration changes, migrations, etc. -->


### Prerequisites
<!-- List any prerequisites for deploying this change -->
- [ ]
- [ ]

### Configuration Changes
<!-- List any environment variables, config files, or settings that need to be updated -->


### Database Migrations
<!-- Describe any database schema changes or data migrations required -->


## Rollback Plan
<!-- Describe how to rollback this change if something goes wrong -->


## Additional Context
<!-- Add any other context, screenshots, logs, or information about the PR here -->


---

## Reviewer Notes
<!-- For reviewers: areas of focus, specific concerns, or questions -->


## Post-Merge Tasks
<!-- Tasks to complete after merging, if any -->
- [ ]
- [ ]
