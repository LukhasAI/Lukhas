---
status: ready-to-execute
type: jules-task-execution
owner: agi_dev
created: 2025-11-01
---

# Jules Task 1 Execution: Admin Authentication (#584)

## ✅ Prerequisites Complete

- [x] Jules API key configured in `.env` ✅
- [x] 7 Codex PRs merged successfully ✅
- [x] Smoke tests passing (10/10 + MATRIZ 3/3) ✅
- [x] System ready for Jules execution ✅

**PR #792 Status**: Deferred for manual review (75k additions, 201 files - mostly generated security artifacts)

---

## 🚀 Execute Jules Task 1 Now

### Option A: Jules CLI Execution

```bash
# Load API key from .env
source .env

# Execute Task 1 using the complete prompt below
jules \
  --repo https://github.com/LukhasAI/Lukhas \
  --issue 584 \
  --branch feat/admin-auth-584 \
  --prompt "$(cat <<'EOF'
TASK: Implement admin authentication for LUKHAS API routing
ISSUE: #584
REPO: https://github.com/LukhasAI/Lukhas
BRANCH: feat/admin-auth-584

CONTEXT:
- Admin routes in lukhas_website/lukhas/api/routing_admin.py need authentication
- Currently has TODO at line 103: "Implement proper admin authentication"
- Must integrate with existing ΛiD identity system in lukhas/identity/
- Follow Protocol pattern from core/ports/openai_provider.py

REQUIREMENTS:

1. CREATE lukhas_website/lukhas/api/middleware/admin_auth.py:
   - AdminAuthMiddleware class
   - Role-based access control (RBAC)
   - Roles: admin, superadmin
   - Integration with ΛiD identity system

2. IMPLEMENT authentication decorator:
   ```python
   from functools import wraps
   from typing import Callable

   def require_admin(roles: list[str] = ["admin"]):
       """Decorator to require admin authentication with specific roles."""
       def decorator(func: Callable):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               # Verify admin authentication
               # Check role permissions
               # Return 401 if not authenticated
               # Return 403 if authenticated but insufficient permissions
               return await func(*args, **kwargs)
           return wrapper
       return decorator
   ```

3. UPDATE lukhas_website/lukhas/api/routing_admin.py:
   - Apply @require_admin decorator to admin routes
   - Remove TODO at line 103
   - Add proper error responses (401/403)

4. CREATE tests/integration/api/test_admin_auth.py:
   - Test admin authentication flow
   - Test role verification (admin vs superadmin)
   - Test 401 response for unauthenticated requests
   - Test 403 response for insufficient permissions
   - Test successful admin access with valid credentials

INTEGRATION POINTS:
- lukhas/identity/ for authentication verification
- governance/guardian/ for policy enforcement (optional)
- observability/metrics.py for auth metrics

FILES TO CREATE:
- lukhas_website/lukhas/api/middleware/admin_auth.py
- lukhas_website/lukhas/api/middleware/__init__.py
- tests/integration/api/test_admin_auth.py

FILES TO MODIFY:
- lukhas_website/lukhas/api/routing_admin.py (line 103)

ACCEPTANCE CRITERIA:
- [ ] AdminAuthMiddleware implemented with RBAC
- [ ] @require_admin decorator working
- [ ] Admin routes protected (return 401/403 appropriately)
- [ ] Integration with ΛiD identity system
- [ ] All integration tests passing
- [ ] Type hints and mypy compliance
- [ ] No hardcoded credentials

COMMANDS TO RUN AFTER IMPLEMENTATION:
```bash
# Run tests
pytest tests/integration/api/test_admin_auth.py -v

# Type check
mypy lukhas_website/lukhas/api/middleware/admin_auth.py

# Run all API tests
pytest tests/integration/api/ -v

# Smoke test
make smoke
```

COMMIT MESSAGE TEMPLATE:
```
feat(api): implement admin authentication with RBAC

Problem:
- Admin routes lacked authentication (lukhas_website/lukhas/api/routing_admin.py:103)
- No role-based access control
- Security risk: unauthenticated admin access

Solution:
- Created AdminAuthMiddleware with RBAC
- Added @require_admin decorator for admin/superadmin roles
- Integrated with ΛiD identity system
- Returns 401/403 appropriately

Impact:
- Secured all admin routes
- Role-based permissions working
- Integration tests verify auth flow
- Closes #584

🤖 Generated with Agent Jules
```

CREATE PR: Yes
PR TITLE: feat(api): implement admin authentication with RBAC (#584)
PR BODY:
```markdown
Implements admin authentication for API admin routes.

## Changes
- ✅ AdminAuthMiddleware with role-based access control
- ✅ @require_admin decorator for route protection
- ✅ Integration with ΛiD identity system
- ✅ 401/403 error responses
- ✅ Integration tests

## Testing
```bash
pytest tests/integration/api/test_admin_auth.py -v
```

## Security Impact
- Secures admin routes requiring authentication
- Role-based permissions (admin, superadmin)
- No hardcoded credentials

Closes #584
```
EOF
)"
```

### Option B: Jules Web Interface

1. Navigate to Jules web UI
2. Paste the complete prompt from the bash command above (everything between the EOF markers)
3. Start execution
4. Monitor progress in real-time

---

## 📊 Monitoring Jules Progress

### Watch for new branch creation
```bash
git fetch origin
git branch -r | grep jules
git branch -r | grep feat/admin-auth-584
```

### Check for PR creation
```bash
gh pr list --author jules
gh pr list --head feat/admin-auth-584
```

### Monitor Jules execution logs
```bash
# If Jules provides logs
tail -f ~/.jules/logs/task-584.log
```

---

## ✅ Review Jules Output

After Jules completes, verify:

1. **Files Created**:
   - [ ] `lukhas_website/lukhas/api/middleware/admin_auth.py`
   - [ ] `lukhas_website/lukhas/api/middleware/__init__.py`
   - [ ] `tests/integration/api/test_admin_auth.py`

2. **Files Modified**:
   - [ ] `lukhas_website/lukhas/api/routing_admin.py` (TODO at line 103 removed)

3. **Implementation Quality**:
   ```bash
   # Pull Jules branch
   git fetch origin feat/admin-auth-584
   git checkout feat/admin-auth-584

   # Run tests
   pytest tests/integration/api/test_admin_auth.py -v

   # Type check
   mypy lukhas_website/lukhas/api/middleware/admin_auth.py

   # Smoke tests
   make smoke
   ```

4. **Security Verification**:
   - [ ] No hardcoded credentials (grep for passwords/keys)
   - [ ] Proper 401/403 responses
   - [ ] Integration with ΛiD identity system
   - [ ] RBAC roles working correctly

5. **PR Quality**:
   - [ ] PR description clear and complete
   - [ ] Commit message follows T4 standards
   - [ ] All acceptance criteria met
   - [ ] CI checks passing (if available)

---

## 🔀 Merge When Ready

```bash
# After review passes
gh pr view <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --admin --subject "feat(api): implement admin authentication with RBAC" --body "Closes #584"

# Update main branch
git checkout main
git pull origin main
```

---

## 📈 Expected Deliverables

- **New Files**: 3 (middleware, __init__, tests)
- **Modified Files**: 1 (routing_admin.py)
- **Lines of Code**: ~200-300 (middleware + tests)
- **Tests**: 5-7 integration tests
- **Issue Closed**: #584
- **Estimated Time**: 3-4 hours

---

## 🎯 Next Steps After Task 1

Once Task 1 is complete and merged:

1. **Update GitHub issue #584** → Close as completed
2. **Update delegation plan** with Task 1 completion status
3. **Launch Jules Task 2** (#581 WebAuthn Challenge/Verify, 5 hours)
4. **Continue sequential execution** through remaining 6 Jules tasks

**Projected Timeline**:
- Day 1 (Nov 1): Tasks 1-2 complete (9 hours)
- Day 2 (Nov 2): Tasks 3-4 complete (7 hours)
- Day 3-4 (Nov 3-4): Tasks 5-6 complete (11 hours)
- Day 5 (Nov 5): Task 7 optional (6 hours)

---

## 🚨 Troubleshooting

### If Jules fails to start:
1. Check API key: `echo $JULES_API_KEY`
2. Verify `.env` file: `cat .env | grep JULES`
3. Test Jules connection: `jules --version` or `jules --help`

### If Jules creates incorrect code:
1. Review the prompt for clarity
2. Add more specific examples from codebase
3. Reference existing patterns explicitly
4. Re-run with refined prompt

### If tests fail:
1. Check imports and dependencies
2. Verify type hints match actual usage
3. Review test assertions
4. Run single test: `pytest path/to/test.py::test_name -v`

---

## 📚 Reference Documentation

- **Main Delegation Plan**: [AGENT_DELEGATION_PLAN_2025-11-01.md](./AGENT_DELEGATION_PLAN_2025-11-01.md)
- **Jules Setup Guide**: [JULES_AGENT_SETUP.md](./JULES_AGENT_SETUP.md)
- **Orchestration Guide**: [MULTI_AGENT_ORCHESTRATION_GUIDE.md](./MULTI_AGENT_ORCHESTRATION_GUIDE.md)
- **Next Steps**: [NEXT_STEPS_EXECUTION.md](./NEXT_STEPS_EXECUTION.md)

---

**🎯 READY TO EXECUTE! Copy the command from Option A or use the web interface with Option B.**
