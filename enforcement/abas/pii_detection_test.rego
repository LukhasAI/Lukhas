package abas.pii_detection_test

# Test that PII redaction triggers for an email
test_redact_email {
    input := {"request": {"body": "Contact: bob@example.com"}}
    act := data.abas.pii_detection.pii_action with input as input
    act.action == "redact"
    act.matches[_] == "email"
}

# Test that phone numbers get detected
test_redact_phone {
    input := {"request": {"body": "Call me at +441234567890"}}
    act := data.abas.pii_detection.pii_action with input as input
    act.action == "redact"
    act.matches[_] == "phone"
}

# Test that special categories produce deny
test_deny_special_category {
    input := {"request": {"body": "I am gay and looking for support."}}
    act := data.abas.pii_detection.pii_action with input as input
    act.action == "deny"
    act.reason == "special_category_detected"
}
