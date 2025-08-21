"""
Provider-Side Plugin Integration Guide

This document outlines the integration specifications for healthcare provider systems
to connect with the Health Advisor Plugin.

Supported Systems:
- Epic Systems
- Cerner
- Allscripts
- eClinicalWorks
- NextGen Healthcare
- Athenahealth
- Custom EHR Systems

Integration Methods:
1. Direct API Integration
2. FHIR-based Integration
3. HL7 Integration
4. Custom Middleware Solutions

Security Requirements:
- HIPAA Compliance
- End-to-end Encryption
- Audit Logging
- Access Control
- Data Privacy Controls
"""

INTEGRATION_GUIDE = {
    "version": "1.0.0",
    "last_updated": "2025-05-25",
    "api_specification": "OpenAPI 3.0",
    "authentication": {
        "methods": ["OAuth2.0", "JWT"],
        "token_endpoint": "/api/v1/auth/token",
        "refresh_endpoint": "/api/v1/auth/refresh"
    },
    "endpoints": {
        "case_notification": "/api/v1/provider/cases/notify",
        "case_update": "/api/v1/provider/cases/{case_id}/update",
        "patient_data_sync": "/api/v1/provider/patients/sync",
        "consultation_session": "/api/v1/provider/consultation/session"
    },
    "data_formats": {
        "patient_record": "FHIR R4",
        "clinical_notes": "HL7 CDA",
        "prescriptions": "NCPDP SCRIPT"
    }
}
