# LUKHΛS  — Python SDK

## Install (local)
```bash
cd sdk/python
pip install -e .
```

## Usage

```python
from lukhas import Lukhas

client = Lukhas("http://127.0.0.1:8000", api_key="dev-key")

# Feedback
client.feedback_card(target_action_id="A-123", rating=5, note="great")
lut = client.feedback_lut()

# Tools
names = client.tools_names()
registry = client.tools_registry()

# DNA
health = client.dna_health()
cmp = client.dna_compare("policy:modulation")

# Admin
summary = client.admin_summary()

print("Audit:", client.audit_view_url("A-XYZ"))
```
