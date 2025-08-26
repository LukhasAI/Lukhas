# MΛTRIZ Brand Guidelines

## Official Product Name

**MΛTRIZ** (formerly MATADA) - Multimodal Adaptive Temporal Architecture for Dynamic Awareness

## Naming Conventions

### Display Usage (Marketing, Headers, Logos)
- **Primary**: `MΛTRIZ`
- **Typography**: Greek Lambda (Λ) character (U+039B)
- **Never**: Do not use "MATADA" in any new content

### Plain Text Usage (Body Copy, SEO, Accessibility)
- **Primary**: `Matriz`
- **In sentences**: "Powered by Matriz technology"
- **Alt text**: Always use "Matriz" not "MΛTRIZ"

### Technical References
- **URLs/Paths**: `/matriz` (never `/mλtriz`)
- **Code variables**: `matriz_node`, `MatrizConfig`
- **File names**: `matriz_agent_brief.md`

## Accessibility Requirements

When using the stylized form `MΛTRIZ`:
```html
<h2 aria-label="Matriz">MΛTRIZ</h2>
```

Always provide `aria-label` for screen readers.

## Migration from MATADA

All references to MATADA should be updated:
- `MATADA` → `MΛTRIZ` (display)
- `matada` → `matriz` (plain text)
- `Matada` → `Matriz` (capitalized)

## Product Description

MΛTRIZ is LUKHAS AI's traceability and governance layer that turns model decisions into auditable nodes.

## Visual Identity

- **Colors**: Inherit from Trinity Framework
  - Primary: Purple (#6B46C1)
  - Secondary: Blue (#0EA5E9)
- **Font**: Helvetica Neue (100 weight for Lambda)
- **Logo**: SVG preferred to maintain Lambda weight consistency

## Common Mistakes to Avoid

❌ Using MATADA in new content
❌ Including Λ in URLs or file paths
❌ Forgetting aria-labels for accessibility
❌ Using Latin "A" instead of Greek Lambda "Λ"
✅ Always test with screen readers
✅ Validate with brand_validator.py script
