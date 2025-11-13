# Guardian Exemption Ledger Audit Report

**Date:** 2025-11-12
**Auditor:** Jules

## 1. Overview

This report details the findings of a security audit conducted on the `guardian_exemptions` ledger, the system responsible for tracking overrides and exceptions to the LUKHAS Guardian security policies.

### 1.1. Scope

The audit's scope was to identify security risks within the `guardian_exemptions` system, focusing on:
- **Unauthorized Exemptions**: Overrides granted without the required approvals.
- **Stale Entries**: Outdated exemptions that have not been reviewed or revoked.
- **Missing Justifications**: Overrides that lack a clear, documented rationale.
- **Consent Violations**: Handling of sensitive data (PII, financial) without evidence of user consent.

### 1.2. Methodology

Since direct database access was not available, the audit was performed by:
1.  **Schema Analysis**: A thorough review of the `guardian_exemptions` table schema in `identity/consent/exemption_ledger.sql`.
2.  **Simulated Data Analysis**: A representative dataset was created to model potential real-world entries. This data was then analyzed against the audit criteria derived from the schema and documented business logic in `guardian/emit.py`.

## 2. Findings

The audit identified several categories of security vulnerabilities. The following findings are based on the analysis of the simulated data.

### 2.1. Unauthorized Exemptions

- **Finding 1: Critical Override Missing Second Approver**
  - **Description**: A critical exemption was granted without the required second T4+ approver. The `approver2_id` field was `NULL`.
  - **Risk**: High. Critical overrides are reserved for high-stakes scenarios. Missing a second approver subverts the dual-approval control, increasing the risk of misuse.
  - **Example**:
    ```json
    {
      "id": "e1a7e2a4-...",
      "band": "critical",
      "override_granted": true,
      "approver1_id": "λID-admin-1",
      "approver2_id": null
    }
    ```

### 2.2. Missing Justifications

- **Finding 2: Override Granted Without Justification**
  - **Description**: An exemption was granted with a `NULL` `justification` field.
  - **Risk**: Medium. Without a justification, it is impossible to perform a post-mortem or audit the reason for an override, creating a gap in accountability.
  - **Example**:
    ```json
    {
      "id": "f3b9b8c1-...",
      "override_granted": true,
      "justification": null
    }
    ```

### 2.3. Stale Entries

- **Finding 3: Potentially Stale Exemption**
  - **Description**: An exemption entry was found with a `created_at` timestamp older than 90 days. The system lacks a mechanism for periodic review or automatic expiration of exemptions.
  - **Risk**: Medium. Stale exemptions could represent persistent security bypasses that are no longer required, increasing the attack surface.
  - **Example**:
    ```json
    {
      "id": "a2c4d6e8-...",
      "created_at": "2025-07-15T10:00:00Z"
    }
    ```

### 2.4. Consent Violations

- **Finding 4: Missing User Consent for PII Processing**
  - **Description**: A record involving the processing of Personally Identifiable Information (PII) was found to be missing the `user_consent_timestamp`.
  - **Risk**: High. This represents a potential violation of data privacy regulations (e.g., GDPR, CCPA) and the LUKHAS acceptable use policy.
  - **Example**:
    ```json
    {
      "id": "b4d6e8f0-...",
      "tags": ["pii"],
      "user_consent_timestamp": null,
      "consent_method": null
    }
    ```

## 3. Recommendations

To address the identified risks, the following remediations are recommended:

1.  **Enforce Approval Policies at the Database Layer**:
    - Implement database constraints or triggers to ensure that `approver1_id` is not `NULL` when `override_granted` is `TRUE`.
    - For critical overrides (`band = 'critical'`), ensure both `approver1_id` and `approver2_id` are not `NULL` and are not identical.

2.  **Mandate Justifications**:
    - Modify the `guardian_exemptions` table schema to make the `justification` field `NOT NULL` for any entry where `override_granted` is `TRUE`.

3.  **Implement an Exemption Review and Expiration Policy**:
    - Introduce a `expires_at` timestamp to all new exemptions.
    - Develop a process for the periodic review (e.g., quarterly) of all active exemptions to ensure they are still necessary. Exemptions should be revoked or renewed as part of this process.

4.  **Strengthen Consent Enforcement**:
    - The existing `CHECK` constraint is a good start, but it should be supplemented with application-level checks to provide clearer error feedback to developers.
    - Ensure that all flows handling sensitive data tags (`pii`, `financial`) robustly capture and record user consent.

## 4. Conclusion

The `guardian_exemptions` ledger is a critical component of the LUKHAS security infrastructure. The vulnerabilities identified in this audit, while based on simulated data, highlight potential weaknesses in the current implementation. By implementing the recommendations above, the system's security posture can be significantly improved.
