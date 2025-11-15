package abas.pii_detection

# Returns an object with:
#   { "action": "deny" | "redact" | "none", "matches": [...], "reason": "..." }
# Uses conservative regexes for email, phone, ssn, credit-card-like digit sequences
# and a small keyword list to detect "special categories" (religion, sexual orientation, HIV, politics).

default pii_action = {"action": "none", "matches": [], "reason": "no_pii"}

# Basic presence checks (safe defaults)
emails_found {
    input.request.body != ""
    re_match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", input.request.body)
}

phones_found {
    input.request.body != ""
    re_match("\\+?[0-9][0-9() .-]{6,20}[0-9]", input.request.body)
}

ssn_found {
    input.request.body != ""
    re_match("\\b[0-9]{3}-[0-9]{2}-[0-9]{4}\\b", input.request.body)
}

cc_found {
    input.request.body != ""
    # Cheap heuristic: 13-16 digit sequences (coarse)
    re_match("\\b[0-9]{13,16}\\b", input.request.body)
}

# "Special categories" / sensitive topic keywords — conservative list
special_found {
    input.request.body != ""
    # case-insensitive RE2 with (?i)
    re_match("(?i).*\\b(gay|lesbian|bisexual|transgender|hiv|aids|muslim|christian|jewish|religion|politic|political|ethnicity)\\b.*", input.request.body)
}

# If special categories appear -> deny
pii_action = {"action": "deny", "matches": ["special_category"], "reason": "special_category_detected"} {
    special_found
}

# If no special category but PII is present -> redact
pii_action = {"action": "redact", "matches": matches, "reason": "pii_detected"} {
    (emails_found or phones_found or ssn_found or cc_found)
    matches := [m | m := "email"; emails_found]
             ++ [m | m := "phone"; phones_found]
             ++ [m | m := "ssn"; ssn_found]
             ++ [m | m := "credit_card_like"; cc_found]
}

# Otherwise none
pii_action = {"action": "none", "matches": [], "reason": "no_pii"} {
    not special_found
    not emails_found
    not phones_found
    not ssn_found
    not cc_found
}
