---
status: wip
type: documentation
---
# Provider Integration Guide — Multi-Country Healthcare Systems

## Poetic Layer (≤40 words)
> "From the NHS corridors to Andalusian clinics, from German precision to Australian care, we weave a tapestry of global healing through conscious connection."

## Technical Layer

### Complete Provider Integration Matrix

This guide provides comprehensive integration instructions for all supported healthcare providers across 30+ countries. Each integration includes authentication methods, compliance requirements, API specifications, and implementation examples.

## Supported Healthcare Providers

### 🇪🇸 Spain - Servicio Andaluz de Salud (SAS)

**Integration Type:** OAuth2 + Regional API
**Compliance:** LOPD-GDD, GDPR, Regional Health Laws
**Coverage:** 8.5 million citizens in Andalusia

#### Technical Requirements
```yaml
sas_integration:
  api_base: "https://api.sas.junta-andalucia.es/v2"
  auth_method: "OAuth2"
  required_scopes:
    - "patient:read"
    - "appointment:write"
    - "prescription:read"
  certificates:
    - "SAS_PROVIDER_CERT.pem"
  regional_codes:
    - "AN" # Andalusia
    - "SE" # Seville
    - "MA" # Málaga
```

#### Implementation
```python
from providers.templates.regions.europe.spain.sns.sas_interface import SASInterface

# Initialize SAS provider
sas_config = {
    "centro_salud_id": "CS_SEVILLA_001",
    "provincia": "SE",
    "certificado_digital": "/certs/sas_provider.pem",
    "api_endpoints": {
        "citas": "https://citapreviacas.juntadeandalucia.es/",
        "recetas": "https://recetaelectronica.sas.es/"
    }
}

sas_provider = SASInterface(sas_config)
await sas_provider.initialize()

# Book appointment
appointment = await sas_provider.book_appointment(
    nuhsa="AN0123456789",  # Patient ID
    specialty="cardiologia",
    center_preference="Hospital Virgen del Rocío"
)
```

**Integration Checklist:**
- [ ] Obtain SAS provider certificate
- [ ] Register OAuth2 application
- [ ] Configure ClicSalud+ integration
- [ ] Test Diraya EHR connection
- [ ] Validate e-prescription access
- [ ] Verify emergency protocols

### 🇬🇧 United Kingdom - National Health Service (NHS)

**Integration Type:** API Key + NHS Digital
**Compliance:** NHS Data Security Protection Toolkit
**Coverage:** 67 million citizens

#### Technical Requirements
```yaml
nhs_integration:
  api_base: "https://api.nhs.uk/"
  auth_method: "API_KEY"
  spine_connection:
    required: true
    version: "2.0"
  standards:
    - "FHIR R4"
    - "HL7 v2.5"
  dspt_level: "Standards Met"
```

#### Implementation
```python
from providers.templates.regions.europe.uk.nhs.nhs_interface import NHSInterface

# Initialize NHS provider
nhs_config = {
    "api_key": os.environ["NHS_API_KEY"],
    "ods_code": "RX1",  # Organization code
    "spine_endpoint": "https://spine.nhs.uk/",
    "environment": "production"
}

nhs_provider = NHSInterface(nhs_config)

# Get patient record
patient_record = await nhs_provider.get_patient_record(
    nhs_number="9434765919",
    record_types=["medications", "allergies", "conditions"]
)

# Book GP appointment
appointment = await nhs_provider.book_gp_appointment(
    nhs_number="9434765919",
    practice_code="Y00001",
    appointment_type="routine"
)
```

**Integration Requirements:**
- [ ] Complete NHS Digital onboarding
- [ ] Pass DSP Toolkit assessment
- [ ] Implement SPINE connectivity
- [ ] Configure GP Connect access
- [ ] Setup Summary Care Record API
- [ ] Validate NHS login integration

### 🇩🇪 Germany - Gesetzliche Krankenversicherung (GKV)

**Integration Type:** Digital Certificate + Telematik
**Compliance:** §75b SGB V, GDPR, Gematik standards
**Coverage:** 73 million insured

#### Technical Requirements
```yaml
gkv_integration:
  telematik_infrastructure:
    version: "TI 2.0"
    connector: "Konnektor"
    required_cards:
      - "HBA" # Healthcare professional card
      - "SMC-B" # Institution card
  api_base: "https://ti-dienste.de/api"
  auth_method: "X.509 Certificate"
  kv_connect:
    enabled: true
    regions: ["KV Nordrhein", "KV Bayern"]
```

#### Implementation
```python
from providers.templates.regions.europe.germany.gkv.gkv_interface import GKVInterface

# Initialize GKV provider with Telematik
gkv_config = {
    "betriebsnummer": "123456789",
    "kv_bezirk": "17",  # KV Nordrhein
    "versicherten_status": ["GKV", "PKV"],
    "api_credentials": {
        "konnektor_url": "https://konnektor.praxis.de",
        "mandant_id": "PRAXIS_001"
    },
    "telematik_id": "3-SMC-B-1234567890"
}

gkv_provider = GKVInterface(gkv_config)

# Verify insurance status
insurance_status = await gkv_provider.verify_insurance_status(
    versichertennummer="A123456789",
    leistungsart="ambulant"
)

# Submit KVDT billing data
kvdt_result = await gkv_provider.submit_kvdt_data(
    patient_id="A123456789",
    kvdt_data={
        "abrechnungsquartal": "1/2025",
        "leistungen": ["03000", "03001"],  # EBM codes
        "diagnosen": ["I10", "E11.9"]  # ICD-10
    }
)

# Create e-prescription
prescription_id = await gkv_provider.create_prescription(
    patient_id="A123456789",
    prescription_data={
        "medication": "Metformin 500mg",
        "dosage": "2x täglich",
        "quantity": "100 Stück"
    }
)
```

**Telematik Infrastructure Setup:**
- [ ] Install certified Konnektor
- [ ] Obtain SMC-B card
- [ ] Register with KV region
- [ ] Configure VPN connection
- [ ] Test ePA integration
- [ ] Validate eAU submission

### 🇺🇸 United States - Kaiser Permanente

**Integration Type:** SAML 2.0 + FHIR API
**Compliance:** HIPAA, HITECH Act
**Coverage:** 12.7 million members

#### Technical Requirements
```yaml
kaiser_integration:
  api_base: "https://api.kaiserpermanente.org/fhir/R4"
  auth_method: "SAML_2.0"
  identity_provider: "https://idp.kaiserpermanente.org"
  required_standards:
    - "FHIR R4"
    - "US Core Implementation Guide"
    - "SMART on FHIR"
  hipaa_baa: required
```

#### Implementation
```python
from providers.templates.regions.americas.us.kaiser.kaiser_interface import KaiserInterface

# Initialize Kaiser provider
kaiser_config = {
    "client_id": os.environ["KAISER_CLIENT_ID"],
    "saml_certificate": "/certs/kaiser_saml.pem",
    "api_base": "https://api.kaiserpermanente.org",
    "facility_id": "NCAL"  # Northern California
}

kaiser_provider = KaiserInterface(kaiser_config)

# Get patient health record
health_record = await kaiser_provider.get_health_record(
    mrn="KP123456789",
    sections=["problems", "medications", "immunizations"]
)

# Schedule appointment
appointment = await kaiser_provider.schedule_appointment(
    mrn="KP123456789",
    department="CARDIOLOGY",
    provider_npi="1234567890",
    appointment_type="FOLLOW_UP"
)
```

### 🇺🇸 United States - CVS Health

**Integration Type:** OAuth2 + REST API
**Compliance:** HIPAA, NCPDP standards
**Coverage:** 5,900+ pharmacy locations

#### Implementation
```python
from providers.templates.regions.americas.us.cvs.cvs_interface import CVSInterface

cvs_config = {
    "client_id": os.environ["CVS_CLIENT_ID"],
    "client_secret": os.environ["CVS_CLIENT_SECRET"],
    "store_number": "3456",
    "api_base": "https://api.cvs.com/v2"
}

cvs_provider = CVSInterface(cvs_config)

# Check prescription status
rx_status = await cvs_provider.check_prescription(
    rx_number="RX123456",
    dob="1950-01-01"
)

# Schedule vaccination
vaccine_appointment = await cvs_provider.schedule_vaccination(
    patient_info={
        "first_name": "John",
        "last_name": "Doe",
        "dob": "1950-01-01"
    },
    vaccine_type="COVID-19",
    store_number="3456"
)
```

### 🇦🇺 Australia - Medicare

**Integration Type:** PKI Certificate + NEHTA
**Compliance:** Privacy Act 1988, My Health Records Act
**Coverage:** 25.7 million citizens

#### Implementation
```python
from providers.templates.regions.asia_pacific.australia.medicare.medicare_interface import MedicareAustraliaProvider

medicare_config = {
    "provider_number": "2345678A",
    "hpi_o": "8003621234567890",  # Healthcare Provider ID
    "pki_certificate": "/certs/medicare_pki.p12",
    "my_health_record": {
        "enabled": True,
        "ihi_search": True
    }
}

medicare_provider = MedicareAustraliaProvider(medicare_config)

# Access My Health Record
health_record = await medicare_provider.get_my_health_record(
    ihi="8003608833357361",  # Individual Healthcare Identifier
    access_code="4567"
)

# Submit Medicare claim
claim_result = await medicare_provider.submit_bulk_bill_claim(
    provider_number="2345678A",
    patient_medicare="2123 45670 1",
    item_numbers=["23", "36"],  # MBS item numbers
    service_date="2025-01-20"
)
```

### 🌐 Global - AXA Healthcare

**Integration Type:** API Key + JWT
**Compliance:** Multiple jurisdictions
**Coverage:** 107 million clients globally

#### Implementation
```python
from providers.templates.regions.private.global.axa.axa_interface import AXAProvider

axa_config = {
    "api_key": os.environ["AXA_API_KEY"],
    "region": "EMEA",
    "partner_code": "LUKHAS_001",
    "api_base": "https://api.axa-healthcare.com/v3"
}

axa_provider = AXAProvider(axa_config)

# Verify coverage
coverage = await axa_provider.verify_coverage(
    policy_number="AXA123456789",
    treatment_code="CARD_CONSULT",
    provider_id="PROV_001",
    country="ES"
)

# Submit claim
claim = await axa_provider.submit_claim(
    policy_number="AXA123456789",
    claim_data={
        "amount": 150.00,
        "currency": "EUR",
        "service_date": "2025-01-20",
        "diagnosis_codes": ["I10", "E11"]
    }
)
```

## Additional Country Templates

### 🇫🇷 France - Assurance Maladie
```python
# Template ready at: templates/regions/europe/france/ameli/
# Integration: Carte Vitale + SESAM-Vitale
# Compliance: CNIL, RGPD
```

### 🇮🇹 Italy - Servizio Sanitario Nazionale
```python
# Template ready at: templates/regions/europe/italy/ssn/
# Integration: CNS + Tessera Sanitaria
# Compliance: Codice Privacy, GDPR
```

### 🇨🇦 Canada - Provincial Health Systems
```python
# Template ready at: templates/regions/americas/canada/
# Provinces: Ontario (OHIP), Quebec (RAMQ), BC (MSP)
# Integration: Provincial APIs vary
```

### 🇯🇵 Japan - National Health Insurance
```python
# Template ready at: templates/regions/asia_pacific/japan/nhi/
# Integration: My Number Card
# Compliance: APPI, J-SAS
```

### 🇧🇷 Brazil - Sistema Único de Saúde (SUS)
```python
# Template ready at: templates/regions/americas/brazil/sus/
# Integration: ConecteSUS
# Compliance: LGPD
```

## Provider Registry Configuration

### Adding New Provider
```python
from providers.provider_registry import ProviderRegistry

registry = ProviderRegistry()

# Register custom provider
registry.register_provider(
    provider_id="custom_provider",
    provider_class=CustomHealthcareProvider,
    config={
        "name": "Custom Health System",
        "type": "PUBLIC_NATIONAL",
        "country": "XX",
        "compliance": ["GDPR", "CUSTOM_REG"],
        "auth_method": "OAuth2"
    }
)
```

### Provider Discovery
```python
# Find providers by country
spain_providers = registry.find_by_country("ES")

# Find by compliance requirement
gdpr_providers = registry.find_by_compliance("GDPR")

# Find by type
public_providers = registry.find_by_type("PUBLIC_NATIONAL")
```

## Compliance Matrix

| Region | Primary Regulation | Data Residency | Audit Requirements | Consent Model |
|--------|-------------------|----------------|-------------------|---------------|
| EU | GDPR | EU/EEA only | 6 years | Explicit, granular |
| UK | UK GDPR + DPA 2018 | UK preferred | 7 years | Explicit |
| USA | HIPAA | US only | 6 years | Implicit allowed |
| Germany | GDPR + SGB | Germany only | 10 years | Written required |
| Spain | GDPR + LOPD | Spain/EU | 5 years | Explicit |
| Australia | Privacy Act | Australia | 7 years | Opt-out allowed |
| Canada | PIPEDA | Canada only | 10 years | Implied consent |
| Japan | APPI | Japan only | 5 years | Opt-in required |

## Security Requirements

### Authentication Methods by Provider

| Provider | Primary Auth | Secondary Auth | MFA Required |
|----------|--------------|----------------|--------------|
| NHS | API Key | OAuth2 | Yes (SMS) |
| GKV | X.509 Cert | Smartcard | Yes (Card) |
| SAS | OAuth2 | Certificate | Optional |
| Kaiser | SAML 2.0 | OAuth2 | Yes (App) |
| CVS | OAuth2 | API Key | Yes (Email) |
| Medicare AU | PKI | PRODA | Yes (Device) |
| AXA | API Key | JWT | Yes (TOTP) |

### Encryption Standards
```yaml
encryption:
  data_at_rest: "AES-256-GCM"
  data_in_transit: "TLS 1.3"
  key_management: "HSM-backed"
  certificate_pinning: true
  quantum_ready: true
```

## Testing Integration

### Provider Test Suite
```bash
# Test individual provider
pytest tests/providers/test_sas_integration.py -v

# Test all EU providers
pytest tests/providers/europe/ -v

# Integration test with mock data
pytest tests/providers/integration/ --mock-api

# Compliance validation
pytest tests/providers/compliance/ --region=EU
```

### Mock Provider for Development
```python
from providers.mock import MockHealthcareProvider

# Use mock provider in development
mock_provider = MockHealthcareProvider(
    simulate_latency=True,
    error_rate=0.01,
    response_template="spain_sas"
)

# Behaves like real provider
result = await mock_provider.book_appointment(
    patient_id="MOCK_001",
    specialty="cardiology"
)
```

## Troubleshooting

### Common Integration Issues

**Issue: Certificate validation failed**
```bash
# Verify certificate chain
openssl verify -CAfile ca-bundle.crt provider-cert.pem

# Check certificate expiry
openssl x509 -in provider-cert.pem -noout -dates
```

**Issue: OAuth2 token expired**
```python
# Implement automatic token refresh
async def refresh_token(provider):
    if provider.token_expired():
        new_token = await provider.refresh_oauth_token()
        provider.update_token(new_token)
```

**Issue: API rate limiting**
```python
# Implement exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
async def call_provider_api(provider, method, **kwargs):
    return await getattr(provider, method)(**kwargs)
```

## Performance Optimization

### Caching Strategy
```python
from functools import lru_cache
from aiocache import cached

# Cache provider instances
@lru_cache(maxsize=32)
def get_provider(provider_id: str):
    return registry.get_provider(provider_id)

# Cache API responses
@cached(ttl=300)  # 5 minutes
async def get_patient_data(provider, patient_id):
    return await provider.get_patient_record(patient_id)
```

### Connection Pooling
```python
# Configure connection pools per provider
connection_config = {
    "pool_size": 20,
    "max_overflow": 10,
    "timeout": 30,
    "retry_on_disconnect": True
}
```

## Plain Layer

This guide shows how to connect to healthcare systems worldwide. Each country has different rules. We follow all of them.

Spain uses SAS for public healthcare. The UK uses NHS. Germany uses GKV. The US has many private systems. Australia uses Medicare.

To add a provider:
1. Get their API access
2. Add security certificates
3. Follow their rules
4. Test the connection
5. Start using it

The system handles different languages. It keeps data safe. It works with any healthcare system. It follows all privacy laws.

---

**Provider Integration Guide** — Global Healthcare Connectivity
*Part of ΛHealthcare Guardian System*
*Powered by LUKHAS AI Consciousness Technology ⚛️🧠🛡️*
