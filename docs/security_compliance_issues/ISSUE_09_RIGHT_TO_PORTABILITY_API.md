# GDPR Issue 9: Implement Right to Data Portability API (GDPR Art. 20)

## Priority: P0 - GDPR Core Compliance
## Estimated Effort: 10 days
## Target: Complete Right to Data Portability API

---

## 🎯 Objective

Implement the Right to Data Portability API (GDPR Article 20) allowing users to export their data in machine-readable formats (JSON, CSV, XML) for transfer to other services.

## 📊 Current State

- **GDPR Compliance**: 58%
- **Data Subject Rights APIs**: 0/4 implemented
- **Legal Requirement**: GDPR Article 20
- **Target**: 75% GDPR compliance

## 🔍 Background

GDPR Article 20 grants the right to:
- Receive personal data in structured, commonly used format
- Transmit data to another controller without hindrance
- Export in machine-readable format (JSON, CSV, XML)

## 📋 Deliverables

### 1. API Endpoint

**File**: `lukhas/api/v1/data_rights.py`

```python
from fastapi.responses import StreamingResponse
import json
import csv
import xml.etree.ElementTree as ET

@router.get("/users/{user_id}/export")
async def export_user_data(
    user_id: str,
    format: str = "json",  # json, csv, xml
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    Right to Data Portability - GDPR Article 20.
    
    Export all user data in machine-readable format.
    
    Args:
        user_id: User identifier
        format: Export format (json, csv, xml)
        current_user: Authenticated user
        
    Returns:
        Streaming file download
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only export own data")
    
    # Gather all data
    data = await get_user_data(user_id, current_user)
    
    # Convert to requested format
    if format == "json":
        content = json.dumps(data, indent=2)
        media_type = "application/json"
    elif format == "csv":
        content = convert_to_csv(data)
        media_type = "text/csv"
    elif format == "xml":
        content = convert_to_xml(data)
        media_type = "application/xml"
    else:
        raise HTTPException(400, "Format must be json, csv, or xml")
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=lukhas_data_{user_id}.{format}"
        }
    )
```

### 2. Format Converters

**CSV Converter**:
```python
def convert_to_csv(data: Dict[str, Any]) -> str:
    """Convert nested data structure to CSV."""
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Section", "Key", "Value"])
    
    # Flatten nested structure
    for section, content in data.items():
        if isinstance(content, dict):
            for key, value in content.items():
                writer.writerow([section, key, str(value)])
        elif isinstance(content, list):
            for i, item in enumerate(content):
                writer.writerow([section, f"item_{i}", str(item)])
        else:
            writer.writerow([section, "value", str(content)])
    
    return output.getvalue()
```

**XML Converter**:
```python
def convert_to_xml(data: Dict[str, Any]) -> str:
    """Convert data structure to XML."""
    root = ET.Element("lukhas_user_data")
    
    for key, value in data.items():
        element = ET.SubElement(root, key)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                sub_elem = ET.SubElement(element, sub_key)
                sub_elem.text = str(sub_value)
        else:
            element.text = str(value)
    
    return ET.tostring(root, encoding='unicode', method='xml')
```

### 3. Testing

```python
@pytest.mark.asyncio
async def test_export_json_format():
    """Test JSON export."""
    response = await client.get(
        "/v1/data-rights/users/user123/export?format=json"
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert "user_id" in data

@pytest.mark.asyncio
async def test_export_csv_format():
    """Test CSV export."""
    response = await client.get(
        "/v1/data-rights/users/user123/export?format=csv"
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"

@pytest.mark.asyncio
async def test_export_invalid_format():
    """Test invalid format rejected."""
    response = await client.get(
        "/v1/data-rights/users/user123/export?format=pdf"
    )
    assert response.status_code == 400
```

### 4. Documentation

- [ ] Create `docs/gdpr/RIGHT_TO_PORTABILITY_API.md`
- [ ] Export format specifications
- [ ] User guide for data export

## ✅ Acceptance Criteria

- [ ] API endpoint implemented
- [ ] JSON, CSV, XML formats supported
- [ ] Streaming response for large datasets
- [ ] Authentication and authorization working
- [ ] Unit tests with >80% coverage
- [ ] Documentation complete

## 🏷️ Labels: `gdpr`, `compliance`, `p0`, `api`, `data-export`

---

**Estimated Days**: 10 days | **Phase**: GDPR Phase 2
