// OpenAI glue for creatives (copy helper)
// Use the Responses API for short copy and the Images API for cached creatives.
// This is a server-side helper the Publisher SDK could call before storing to CDN.

import OpenAI from "openai";
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! });

export async function planCreative(opportunity: any, context: any) {
  const system = `You are the NIAS Creative Planner. Output only JSON with {"copy": "...", "image_prompt":"..."}
Rules:
- copy: ≤90 chars, non-manipulative, consent-respectful
- image_prompt: ≤400 chars, brand-safe, product-focused
- Match opportunity domain and user context
- No urgency manipulation ("act now", "limited time")
- No exclusivity manipulation ("secret", "insider only")`;
  
  const resp = await client.responses.create({
    model: "gpt-4.1-mini",
    input: [
      { role: "system", content: system },
      { role: "user", content: JSON.stringify({ opportunity, context }) }
    ],
    response_format: { type: "json_object" }
  });
  
  const { output_text } = resp as any;
  return JSON.parse(output_text);
}

export async function generateImage(image_prompt: string) {
  const img = await client.images.generate({
    model: "gpt-image-1",
    prompt: image_prompt,
    size: "1024x1024"
  });
  return img.data[0].b64_json!;
}

/*
// Usage example:
const creative = await planCreative(
  { domain: "retail.pet_food", title: "Premium Dog Food", price_current: 39.99 },
  { user_has_dog: true, last_purchase: "2 weeks ago" }
);
// Returns: { copy: "Fresh ingredients for happy, healthy dogs", image_prompt: "Premium dog food bag with fresh ingredients, kitchen setting, natural lighting" }

const imageB64 = await generateImage(creative.image_prompt);
// Upload imageB64 to your CDN and reference in Opportunity.media.cdn_url
*/