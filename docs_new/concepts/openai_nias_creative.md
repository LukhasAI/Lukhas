---
title: Openai Nias Creative
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["api", "testing", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic"]
  audience: ["dev"]
---

# OpenAI NIAS Creative Planner Prompt Pack

## System Prompt

```
You are the NIAS Creative Planner. Output only JSON with keys: {"copy":"...", "image_prompt":"..."}.

Rules:
- Copy must be <= 90 chars, declarative, non-manipulative, opt-in tone.
- Avoid urgency terms ("last chance", "hurry") unless `context.urgency=true`.
- Use consent-respectful language ("Ready to restock?", "Spotted a deal", "Found this for you").
- Image prompt must describe a concrete, brand-safe scene. Do not include brand logos unless provided.
- Focus on product utility and value, not emotional manipulation.
- Maintain LUKHAS tone: helpful, transparent, user-first.

Output Format: JSON only. No markdown, no explanations.

Example Good Copy:
- "Ready to restock?"
- "Found this deal for you"
- "Spotted a price drop"
- "Your usual item is available"
- "Matching your preferences"

Example Bad Copy:
- "URGENT: Last chance!"
- "You NEED this now!"
- "Limited time only!"
- "Don't miss out!"
- "Act fast before it's gone!"

Image Prompt Guidelines:
- Describe the product in natural, appealing context
- Include relevant lifestyle elements
- Avoid logos, brand names, or copyrighted elements
- Focus on product utility and appeal
- Keep descriptions concrete and specific
```

## Example Interactions

### Example 1: Pet Food Restock

**User Input:**
```json
{
  "opportunity": {
    "id": "opp_restock_acme_dog_food_123",
    "domain": "retail.pet_food",
    "title": "Acme Dog Food 10kg - Restock Ready",
    "description": "Your usual Acme Dog Food is running low. Current price $34.50 vs. last $39.90",
    "price_current": 34.50,
    "price_alt": 39.90
  },
  "context": {
    "season": "autumn",
    "style": "warm/minimal",
    "urgency": false
  }
}
```

**Expected Response:**
```json
{
  "copy": "Ready to restock? Found your usual dog food at $34.50",
  "image_prompt": "Premium dog food bag in a clean, modern kitchen setting with a happy golden retriever nearby, warm autumn lighting, minimalist home decor"
}
```

### Example 2: Travel Deal

**User Input:**
```json
{
  "opportunity": {
    "id": "opp_travel_sfo_nyc_456", 
    "domain": "travel.flight",
    "title": "SFO → NYC from $299 - Perfect timing",
    "description": "Morning departures available matching your calendar. 2 weeks advance booking.",
    "price_current": 299.00,
    "price_alt": 450.00
  },
  "context": {
    "season": "spring",
    "style": "professional/clean",
    "urgency": false
  }
}
```

**Expected Response:**
```json
{
  "copy": "SFO → NYC flights from $299. Timing matches your calendar",
  "image_prompt": "Modern airplane flying above clouds from San Francisco skyline toward New York City, professional business travel aesthetic, clean morning light"
}
```

### Example 3: Tech Product with Urgency

**User Input:**
```json
{
  "opportunity": {
    "id": "opp_laptop_deal_789",
    "domain": "tech.laptop", 
    "title": "MacBook Pro M3 - Limited Stock",
    "description": "The laptop you've been tracking is finally in stock at your preferred retailer",
    "price_current": 1999.00,
    "price_alt": 2399.00
  },
  "context": {
    "season": "winter",
    "style": "tech/modern",
    "urgency": true
  }
}
```

**Expected Response:**
```json
{
  "copy": "MacBook Pro M3 back in stock - $1,999 (was $2,399)",
  "image_prompt": "Sleek silver laptop computer on a clean modern desk in a bright workspace, tech professional environment, winter light through windows"
}
```

## Integration Code Examples

### Node.js with OpenAI SDK

```javascript
import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function generateCreative(opportunity, context) {
  const system = `You are the NIAS Creative Planner. Output only JSON with keys: {"copy":"...", "image_prompt":"..."}...`;
  
  const user = JSON.stringify({ opportunity, context });
  
  try {
    const response = await client.chat.completions.create({
      model: "gpt-4-1106-preview", // Use latest GPT-4 model
      messages: [
        { role: "system", content: system },
        { role: "user", content: user }
      ],
      response_format: { type: "json_object" },
      temperature: 0.7,
      max_tokens: 200
    });
    
    return JSON.parse(response.choices[0].message.content);
  } catch (error) {
    console.error('Creative generation failed:', error);
    // Fallback to safe default
    return {
      copy: "Found this for you",
      image_prompt: "Product in clean, minimal setting with soft natural lighting"
    };
  }
}
```

### Python with OpenAI SDK

```python
from openai import OpenAI
import json

client = OpenAI()

def generate_creative(opportunity, context):
    system_prompt = """You are the NIAS Creative Planner..."""
    
    user_input = json.dumps({"opportunity": opportunity, "context": context})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=200
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Creative generation failed: {e}")
        # Fallback to safe default
        return {
            "copy": "Found this for you",
            "image_prompt": "Product in clean, minimal setting with soft natural lighting"
        }
```

## Quality Assurance

### Content Moderation Check

```javascript
// Always run moderation on generated copy
async function moderateContent(copy) {
  try {
    const moderation = await client.moderations.create({
      input: copy,
      model: "text-moderation-stable"
    });
    
    if (moderation.results[0].flagged) {
      return "Found this for you"; // Safe fallback
    }
    
    return copy;
  } catch (error) {
    console.error('Moderation failed:', error);
    return "Found this for you"; // Safe fallback
  }
}
```

### Copy Length Validation

```javascript
function validateCopy(copy) {
  if (copy.length > 90) {
    // Truncate and add ellipsis
    return copy.substring(0, 87) + "...";
  }
  return copy;
}
```

### Tone Validation

```javascript
const forbiddenPhrases = [
  "urgent", "last chance", "hurry", "act fast", "limited time", 
  "don't miss", "you need", "must have", "exclusive offer"
];

function validateTone(copy) {
  const lowerCopy = copy.toLowerCase();
  
  for (const phrase of forbiddenPhrases) {
    if (lowerCopy.includes(phrase.toLowerCase())) {
      return "Found this for you"; // Safe fallback
    }
  }
  
  return copy;
}
```

## Cache Strategy

```javascript
// Cache creative plans to reduce API costs
const creativeCache = new Map();

function getCacheKey(opportunity, context) {
  return `${opportunity.id}_${context.season}_${context.style}_${context.urgency}`;
}

async function getCachedCreative(opportunity, context) {
  const cacheKey = getCacheKey(opportunity, context);
  
  if (creativeCache.has(cacheKey)) {
    return creativeCache.get(cacheKey);
  }
  
  const creative = await generateCreative(opportunity, context);
  creativeCache.set(cacheKey, creative);
  
  return creative;
}
```