"""
Native Content Formatter for NIAS
Makes ads feel like natural content or useful suggestions
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ContentFormat(Enum):
    """Types of native content formats"""

    STORY = "story"  # News feed story format
    SUGGESTION = "suggestion"  # Tool or feature suggestion
    RECOMMENDATION = "recommendation"  # Product recommendation
    TIP = "tip"  # Helpful tip or advice
    NOTIFICATION = "notification"  # System-style notification
    CARD = "card"  # Content card format
    INLINE = "inline"  # Inline text suggestion
    SIDEBAR = "sidebar"  # Sidebar widget
    BANNER = "banner"  # Subtle banner
    CONTEXTUAL = "contextual"  # Context-aware popup


class ContentContext(Enum):
    """Context where content appears"""

    NEWS_FEED = "news_feed"
    SEARCH_RESULTS = "search_results"
    ARTICLE_BREAK = "article_break"
    TOOL_LIMIT = "tool_limit"
    RELATED_ITEMS = "related_items"
    WORKFLOW_COMPLETE = "workflow_complete"
    ERROR_RECOVERY = "error_recovery"
    FEATURE_DISCOVERY = "feature_discovery"
    SOCIAL_FEED = "social_feed"
    DASHBOARD = "dashboard"


@dataclass
class NativeContent:
    """Native-formatted content"""

    content_id: str
    format_type: ContentFormat
    context: ContentContext
    headline: str
    description: str
    visual_url: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    styling: dict[str, Any] = field(default_factory=dict)
    engagement_hints: list[str] = field(default_factory=list)
    reward_preview: Optional[dict] = None


@dataclass
class ContentTemplate:
    """Template for content formatting"""

    template_id: str
    format_type: ContentFormat
    html_template: str
    css_classes: list[str]
    variables: list[str]
    preview_enabled: bool = True


class NativeContentFormatter:
    """
    Formats ads to feel like natural content
    Makes advertising seamless and non-intrusive
    """

    def __init__(self):
        self.templates = self._load_default_templates()
        self.context_rules = self._define_context_rules()
        self.style_presets = self._load_style_presets()
        self.content_cache: dict[str, NativeContent] = {}

    def format_as_native(
        self,
        ad_content: dict[str, Any],
        target_context: ContentContext,
        user_context: Optional[dict[str, Any]] = None,
    ) -> NativeContent:
        """
        Format ad content to match native environment
        """
        # Determine best format for context
        format_type = self._select_format_for_context(target_context, user_context)

        # Extract content elements
        headline = self._generate_native_headline(ad_content, format_type)
        description = self._generate_native_description(ad_content, format_type)

        # Apply contextual adaptation
        adapted_content = self._adapt_to_context(headline, description, target_context, user_context)

        # Generate visual elements
        visual_url = self._process_visual_content(ad_content.get("image_url"))

        # Create CTA that feels natural
        cta_text, cta_url = self._generate_natural_cta(ad_content, format_type, target_context)

        # Apply native styling
        styling = self._apply_native_styling(format_type, target_context)

        # Add engagement hints
        engagement_hints = self._generate_engagement_hints(format_type, user_context)

        # Add reward preview if applicable
        reward_preview = self._generate_reward_preview(ad_content)

        native_content = NativeContent(
            content_id=ad_content.get("id", self._generate_content_id()),
            format_type=format_type,
            context=target_context,
            headline=adapted_content["headline"],
            description=adapted_content["description"],
            visual_url=visual_url,
            cta_text=cta_text,
            cta_url=cta_url,
            metadata=self._extract_metadata(ad_content),
            styling=styling,
            engagement_hints=engagement_hints,
            reward_preview=reward_preview,
        )

        # Cache formatted content
        self.content_cache[native_content.content_id] = native_content

        return native_content

    def format_as_story(self, ad_content: dict[str, Any], feed_style: str = "social") -> dict[str, Any]:
        """
        Format ad as a story in news/social feed
        Appears just like another story
        """
        story = {
            "type": "story",
            "sponsored": True,  # Transparent about sponsorship
            "sponsor_label": "Suggested for you",  # Softer than "Ad"
            "author": {
                "name": ad_content.get("brand_name", "Partner"),
                "avatar": ad_content.get("brand_logo"),
                "verified": True,
            },
            "timestamp": self._generate_natural_timestamp(),
            "headline": self._make_headline_engaging(ad_content.get("title")),
            "preview": self._generate_story_preview(ad_content.get("description")),
            "image": {
                "url": ad_content.get("image_url"),
                "alt": ad_content.get("image_alt", ""),
                "aspect_ratio": "16:9",
            },
            "engagement": {
                "likes": self._generate_social_proof_number(),
                "comments": self._generate_comment_count(),
                "shares": self._generate_share_count(),
            },
            "cta": {
                "text": "Learn More",
                "style": "subtle",
                "reward_hint": "🎁 Earn 5 credits",
            },
            "native_elements": {
                "use_feed_fonts": True,
                "use_feed_spacing": True,
                "use_feed_animations": True,
            },
        }

        # Adapt to feed style
        if feed_style == "news":
            story["category"] = self._select_news_category(ad_content)
            story["read_time"] = "2 min read"
        elif feed_style == "social":
            story["social_context"] = self._generate_social_context()

        return story

    def format_as_suggestion(self, ad_content: dict[str, Any], trigger_context: str) -> dict[str, Any]:
        """
        Format as helpful suggestion at the right moment
        Like tool upgrade when hitting limits
        """
        suggestion = {
            "type": "suggestion",
            "timing": "contextual",
            "trigger": trigger_context,
            "icon": self._select_suggestion_icon(trigger_context),
            "title": self._generate_helpful_title(ad_content, trigger_context),
            "message": self._generate_helpful_message(ad_content, trigger_context),
            "benefits": self._list_relevant_benefits(ad_content, trigger_context),
            "visual": {
                "type": "inline_preview",
                "content": ad_content.get("preview_image"),
            },
            "actions": [
                {
                    "label": self._generate_contextual_cta(trigger_context),
                    "style": "primary",
                    "reward": "10 credits + exclusive access",
                },
                {"label": "Maybe later", "style": "secondary"},
            ],
            "dismissible": True,
            "remember_choice": True,
        }

        # Context-specific adaptations
        if trigger_context == "limit_reached":
            suggestion["urgency"] = "low"
            suggestion["message"] = f"You've been productive! {suggestion['message']}"
        elif trigger_context == "error_occurred":
            suggestion["urgency"] = "medium"
            suggestion["message"] = f"Having trouble? {suggestion['message']}"
        elif trigger_context == "task_complete":
            suggestion["urgency"] = "none"
            suggestion["message"] = f"Great job! {suggestion['message']}"

        return suggestion

    def format_as_related_item(self, ad_content: dict[str, Any], related_to: dict[str, Any]) -> dict[str, Any]:
        """
        Format as related item/accessory
        Appears naturally alongside user's interest
        """
        related_item = {
            "type": "related_item",
            "relationship": self._determine_relationship(ad_content, related_to),
            "presentation": {
                "style": "card",
                "size": "compact",
                "position": "alongside",
            },
            "content": {
                "badge": self._generate_relationship_badge(ad_content, related_to),
                "title": ad_content.get("title"),
                "subtitle": self._generate_relationship_subtitle(ad_content, related_to),
                "image": ad_content.get("thumbnail_url"),
                "price": ad_content.get("price"),
                "rating": ad_content.get("rating"),
                "availability": ad_content.get("availability", "In Stock"),
            },
            "relevance_explanation": self._explain_relevance(ad_content, related_to),
            "social_proof": {
                "text": f"{self._generate_social_proof_number()} people also viewed this",
                "authentic": True,
            },
            "interaction": {
                "hover_preview": True,
                "quick_view": True,
                "save_option": True,
            },
        }

        return related_item

    def adapt_to_platform(self, native_content: NativeContent, platform: str) -> dict[str, Any]:
        """
        Adapt native content to specific platform conventions
        """
        adaptations = {
            "web": self._adapt_for_web,
            "mobile": self._adapt_for_mobile,
            "desktop_app": self._adapt_for_desktop_app,
            "tablet": self._adapt_for_tablet,
            "watch": self._adapt_for_watch,
        }

        adapter = adaptations.get(platform, self._adapt_for_web)
        return adapter(native_content)

    def _load_default_templates(self) -> dict[str, ContentTemplate]:
        """Load default content templates"""
        templates = {}

        # Story template
        templates["story"] = ContentTemplate(
            template_id="story_default",
            format_type=ContentFormat.STORY,
            html_template="""
            <article class="native-story {css_classes}">
                <header class="story-header">
                    <img src="{author_avatar}" class="author-avatar" alt="{author_name}">
                    <div class="author-info">
                        <span class="author-name">{author_name}</span>
                        <span class="story-meta">{timestamp} · Suggested</span>
                    </div>
                </header>
                <div class="story-content">
                    <h3 class="story-headline">{headline}</h3>
                    <p class="story-preview">{preview}</p>
                    <img src="{image_url}" class="story-image" alt="{image_alt}">
                </div>
                <footer class="story-footer">
                    <div class="engagement-stats">
                        <span class="likes">{likes}</span>
                        <span class="comments">{comments}</span>
                    </div>
                    <button class="cta-button">{cta_text}</button>
                </footer>
            </article>
            """,
            css_classes=["native-content", "story-format"],
            variables=[
                "author_avatar",
                "author_name",
                "timestamp",
                "headline",
                "preview",
                "image_url",
                "image_alt",
                "likes",
                "comments",
                "cta_text",
            ],
        )

        # Suggestion template
        templates["suggestion"] = ContentTemplate(
            template_id="suggestion_default",
            format_type=ContentFormat.SUGGESTION,
            html_template="""
            <div class="native-suggestion {css_classes}">
                <div class="suggestion-icon">{icon}</div>
                <div class="suggestion-content">
                    <h4 class="suggestion-title">{title}</h4>
                    <p class="suggestion-message">{message}</p>
                    <ul class="suggestion-benefits">
                        {benefits_list}
                    </ul>
                </div>
                <div class="suggestion-actions">
                    <button class="primary-action">{primary_cta}</button>
                    <button class="secondary-action">{secondary_cta}</button>
                </div>
            </div>
            """,
            css_classes=["native-content", "suggestion-format"],
            variables=[
                "icon",
                "title",
                "message",
                "benefits_list",
                "primary_cta",
                "secondary_cta",
            ],
        )

        return templates

    def _define_context_rules(self) -> dict[ContentContext, dict]:
        """Define rules for each context"""
        return {
            ContentContext.NEWS_FEED: {
                "preferred_formats": [ContentFormat.STORY, ContentFormat.CARD],
                "max_frequency": 1,  # 1 ad per 10 real stories
                "position_rule": "every_10th",
            },
            ContentContext.TOOL_LIMIT: {
                "preferred_formats": [ContentFormat.SUGGESTION, ContentFormat.TIP],
                "trigger": "limit_reached",
                "delay": 2.0,  # Wait 2 seconds after limit
            },
            ContentContext.RELATED_ITEMS: {
                "preferred_formats": [ContentFormat.RECOMMENDATION, ContentFormat.CARD],
                "max_items": 3,
                "relevance_threshold": 0.7,
            },
        }

    def _load_style_presets(self) -> dict[str, dict]:
        """Load styling presets for different formats"""
        return {
            "story": {
                "font_family": "inherit",
                "border": "none",
                "background": "var(--card-background)",
                "padding": "var(--card-padding)",
                "margin": "var(--card-margin)",
                "border_radius": "var(--card-radius)",
                "box_shadow": "var(--card-shadow)",
            },
            "suggestion": {
                "background": "var(--suggestion-bg)",
                "border": "1px solid var(--suggestion-border)",
                "padding": "12px 16px",
                "margin": "8px 0",
                "border_radius": "8px",
                "animation": "slideIn 0.3s ease",
            },
            "inline": {
                "display": "inline-block",
                "padding": "4px 8px",
                "background": "var(--highlight-bg)",
                "border_radius": "4px",
                "font_size": "inherit",
            },
        }

    def _select_format_for_context(self, context: ContentContext, user_context: Optional[dict]) -> ContentFormat:
        """Select best format for given context"""
        rules = self.context_rules.get(context, {})
        preferred = rules.get("preferred_formats", [ContentFormat.CARD])

        # User preference override
        if user_context and "preferred_format" in user_context:
            user_pref = ContentFormat(user_context["preferred_format"])
            if user_pref in preferred:
                return user_pref

        return preferred[0] if preferred else ContentFormat.CARD

    def _generate_native_headline(self, ad_content: dict, format_type: ContentFormat) -> str:
        """Generate headline that feels native"""
        base_headline = ad_content.get("title", "")

        if format_type == ContentFormat.STORY:
            # Make it news-like
            return self._make_headline_engaging(base_headline)
        elif format_type == ContentFormat.SUGGESTION:
            # Make it helpful
            return f"Tip: {base_headline}"
        elif format_type == ContentFormat.RECOMMENDATION:
            # Make it personal
            return f"Recommended: {base_headline}"

        return base_headline

    def _generate_native_description(self, ad_content: dict, format_type: ContentFormat) -> str:
        """Generate description that feels native"""
        base_desc = ad_content.get("description", "")

        if format_type == ContentFormat.STORY:
            # Add context
            return f"{base_desc[:150]}..."
        elif format_type == ContentFormat.SUGGESTION:
            # Make it actionable
            return f"Here's how: {base_desc}"

        return base_desc

    def _adapt_to_context(
        self,
        headline: str,
        description: str,
        context: ContentContext,
        user_context: Optional[dict],
    ) -> dict[str, str]:
        """Adapt content to specific context"""
        adapted = {"headline": headline, "description": description}

        if context == ContentContext.TOOL_LIMIT:
            adapted["headline"] = f"Unlock More: {headline}"
            adapted["description"] = f"You've reached your limit. {description}"
        elif context == ContentContext.WORKFLOW_COMPLETE:
            adapted["headline"] = f"Well Done! {headline}"
            adapted["description"] = f"Now that you're finished, {description}"
        elif context == ContentContext.ERROR_RECOVERY:
            adapted["headline"] = f"Need Help? {headline}"
            adapted["description"] = f"We noticed an issue. {description}"

        return adapted

    def _generate_natural_cta(
        self, ad_content: dict, format_type: ContentFormat, context: ContentContext
    ) -> tuple[str, str]:
        """Generate CTA that feels natural"""
        url = ad_content.get("url", "")

        cta_text_map = {
            ContentFormat.STORY: "Read More",
            ContentFormat.SUGGESTION: "Try It",
            ContentFormat.RECOMMENDATION: "View",
            ContentFormat.TIP: "Learn How",
            ContentFormat.NOTIFICATION: "Details",
        }

        cta_text = cta_text_map.get(format_type, "Learn More")

        # Add reward hint
        if ad_content.get("reward_value"):
            cta_text += f" (Earn {ad_content['reward_value']} credits)"

        return cta_text, url

    def _apply_native_styling(self, format_type: ContentFormat, context: ContentContext) -> dict[str, Any]:
        """Apply native platform styling"""
        base_style = self.style_presets.get(format_type.value, {})

        # Context-specific adjustments
        if context == ContentContext.NEWS_FEED:
            base_style["blend_mode"] = "seamless"
        elif context == ContentContext.SIDEBAR:
            base_style["position"] = "sticky"

        return base_style

    def _generate_engagement_hints(self, format_type: ContentFormat, user_context: Optional[dict]) -> list[str]:
        """Generate hints to encourage engagement"""
        hints = []

        if format_type == ContentFormat.STORY:
            hints.append("Trending in your interests")
        elif format_type == ContentFormat.SUGGESTION:
            hints.append("Users like you found this helpful")

        if user_context and user_context.get("interests"):
            hints.append(f"Related to {user_context['interests'][0]}")

        return hints

    def _generate_reward_preview(self, ad_content: dict) -> Optional[dict]:
        """Generate preview of rewards for engagement"""
        if not ad_content.get("rewards_enabled"):
            return None

        return {
            "credits": ad_content.get("reward_credits", 5),
            "points": ad_content.get("reward_points", 10),
            "exclusive": ad_content.get("unlocks_content", False),
            "preview_text": "Earn rewards for engaging",
        }

    def _process_visual_content(self, image_url: Optional[str]) -> Optional[str]:
        """Process and optimize visual content"""
        if not image_url:
            return None

        # Add CDN/optimization parameters
        if "?" in image_url:
            return f"{image_url}&optimize=true&format=webp"
        return f"{image_url}?optimize=true&format=webp"

    def _extract_metadata(self, ad_content: dict) -> dict:
        """Extract relevant metadata"""
        return {
            "advertiser": ad_content.get("advertiser"),
            "campaign": ad_content.get("campaign_id"),
            "category": ad_content.get("category"),
            "targeting": ad_content.get("targeting_params", {}),
        }

    def _generate_content_id(self) -> str:
        """Generate unique content ID"""
        import uuid

        return f"native_{uuid.uuid4().hex[:8]}"

    def _generate_natural_timestamp(self) -> str:
        """Generate natural-looking timestamp"""
        import random

        minutes = random.randint(2, 59)
        return f"{minutes} minutes ago"

    def _make_headline_engaging(self, title: str) -> str:
        """Make headline more engaging"""
        if not title:
            return "Something interesting for you"

        # Add intrigue
        if not any(word in title.lower() for word in ["how", "why", "what", "when"]):
            return f"Discover: {title}"

        return title

    def _generate_story_preview(self, description: str) -> str:
        """Generate story preview text"""
        if not description:
            return "Check out this interesting content we think you'll enjoy."

        # Truncate and add ellipsis
        if len(description) > 150:
            return f"{description[:147]}..."

        return description

    def _generate_social_proof_number(self) -> str:
        """Generate realistic social proof numbers"""
        import random

        base = random.randint(100, 5000)
        if base > 1000:
            return f"{base/1000:.1f}K"
        return str(base)

    def _generate_comment_count(self) -> int:
        """Generate realistic comment count"""
        import random

        return random.randint(5, 150)

    def _generate_share_count(self) -> int:
        """Generate realistic share count"""
        import random

        return random.randint(10, 500)

    def _select_news_category(self, ad_content: dict) -> str:
        """Select appropriate news category"""
        category = ad_content.get("category", "general")
        category_map = {
            "tech": "Technology",
            "business": "Business",
            "lifestyle": "Lifestyle",
            "entertainment": "Entertainment",
            "health": "Health & Wellness",
        }
        return category_map.get(category, "Trending")

    def _generate_social_context(self) -> str:
        """Generate social context for feed"""
        contexts = [
            "Friends are talking about this",
            "Popular in your network",
            "Recommended by experts",
            "Trending topic",
        ]
        import random

        return random.choice(contexts)

    def _select_suggestion_icon(self, trigger: str) -> str:
        """Select appropriate icon for suggestion"""
        icons = {
            "limit_reached": "🚀",
            "error_occurred": "💡",
            "task_complete": "🎉",
            "feature_discovery": "✨",
            "upgrade_available": "⬆️",
        }
        return icons.get(trigger, "💡")

    def _generate_helpful_title(self, ad_content: dict, trigger: str) -> str:
        """Generate helpful title based on trigger"""
        base_title = ad_content.get("title", "")

        if trigger == "limit_reached":
            return f"Go Beyond Limits with {base_title}"
        elif trigger == "error_occurred":
            return f"Solve This with {base_title}"
        elif trigger == "task_complete":
            return f"You Might Also Like {base_title}"

        return base_title

    def _generate_helpful_message(self, ad_content: dict, trigger: str) -> str:
        """Generate helpful message based on context"""
        base_msg = ad_content.get("description", "")

        if trigger == "limit_reached":
            return f"You're doing great! {base_msg}"
        elif trigger == "error_occurred":
            return f"Let us help. {base_msg}"

        return base_msg

    def _list_relevant_benefits(self, ad_content: dict, trigger: str) -> list[str]:
        """List benefits relevant to trigger context"""
        benefits = ad_content.get("benefits", [])

        if trigger == "limit_reached":
            benefits.insert(0, "Unlimited access")
        elif trigger == "error_occurred":
            benefits.insert(0, "Instant solution")

        return benefits[:3]  # Limit to 3 most relevant

    def _generate_contextual_cta(self, trigger: str) -> str:
        """Generate context-appropriate CTA"""
        cta_map = {
            "limit_reached": "Upgrade Now",
            "error_occurred": "Get Help",
            "task_complete": "Explore More",
            "feature_discovery": "Try It Out",
        }
        return cta_map.get(trigger, "Learn More")

    def _determine_relationship(self, ad_content: dict, related_to: dict) -> str:
        """Determine relationship between items"""
        # Check for direct relationships
        if ad_content.get("category") == related_to.get("category"):
            return "similar"

        if ad_content.get("brand") == related_to.get("brand"):
            return "same_brand"

        if "accessory" in ad_content.get("tags", []):
            return "accessory"

        return "complementary"

    def _generate_relationship_badge(self, ad_content: dict, related_to: dict) -> str:
        """Generate badge explaining relationship"""
        rel = self._determine_relationship(ad_content, related_to)

        badges = {
            "similar": "Similar Item",
            "same_brand": "Same Brand",
            "accessory": "Goes Well With",
            "complementary": "You Might Also Like",
        }

        return badges.get(rel, "Related")

    def _generate_relationship_subtitle(self, ad_content: dict, related_to: dict) -> str:
        """Generate subtitle explaining relationship"""
        rel = self._determine_relationship(ad_content, related_to)

        if rel == "accessory":
            return f"Perfect companion for your {related_to.get('title', 'selection')}"
        elif rel == "same_brand":
            return f"More from {ad_content.get('brand', 'this brand')}"

        return "Based on your interests"

    def _explain_relevance(self, ad_content: dict, related_to: dict) -> str:
        """Explain why this item is relevant"""
        reasons = []

        if ad_content.get("category") == related_to.get("category"):
            reasons.append("in the same category")

        if ad_content.get("price_range") == related_to.get("price_range"):
            reasons.append("similar price range")

        if not reasons:
            return "Customers who viewed this also viewed"

        return f"Suggested because it's {' and '.join(reasons)}"

    def _adapt_for_web(self, content: NativeContent) -> dict:
        """Adapt content for web platform"""
        return {
            "html": self._render_html(content),
            "css": self._generate_css(content),
            "responsive": True,
            "lazy_load": True,
        }

    def _adapt_for_mobile(self, content: NativeContent) -> dict:
        """Adapt content for mobile platform"""
        return {
            "layout": "vertical",
            "swipeable": True,
            "touch_optimized": True,
            "compact_mode": True,
        }

    def _adapt_for_desktop_app(self, content: NativeContent) -> dict:
        """Adapt content for desktop application"""
        return {"windowed": False, "native_controls": True, "keyboard_shortcuts": True}

    def _adapt_for_tablet(self, content: NativeContent) -> dict:
        """Adapt content for tablet"""
        return {
            "layout": "adaptive",
            "orientation_aware": True,
            "touch_and_pointer": True,
        }

    def _adapt_for_watch(self, content: NativeContent) -> dict:
        """Adapt content for smartwatch"""
        return {"glanceable": True, "minimal_text": True, "haptic_feedback": True}

    def _render_html(self, content: NativeContent) -> str:
        """Render content as HTML"""
        template = self.templates.get(content.format_type.value)
        if not template:
            return ""

        # Simple template rendering
        html = template.html_template
        # Would implement actual template rendering here
        return html

    def _generate_css(self, content: NativeContent) -> str:
        """Generate CSS for content"""
        styles = content.styling
        css_rules = []

        for prop, value in styles.items():
            css_prop = prop.replace("_", "-")
            css_rules.append(f"{css_prop}: {value};")

        return " ".join(css_rules)


# Example usage
if __name__ == "__main__":
    formatter = NativeContentFormatter()

    # Example ad content
    ad_content = {
        "id": "ad_123",
        "title": "Premium Analytics Tool",
        "description": "Get deeper insights into your data with advanced analytics",
        "image_url": "https://example.com/analytics.jpg",
        "url": "https://example.com/upgrade",
        "brand_name": "DataPro",
        "brand_logo": "https://example.com/logo.jpg",
        "category": "tech",
        "rewards_enabled": True,
        "reward_credits": 10,
        "benefits": ["Real-time data", "Custom dashboards", "AI insights"],
    }

    # Format as story for news feed
    story = formatter.format_as_story(ad_content, feed_style="news")
    print("Story format:", json.dumps(story, indent=2))

    # Format as suggestion when limit reached
    suggestion = formatter.format_as_suggestion(ad_content, "limit_reached")
    print("\nSuggestion format:", json.dumps(suggestion, indent=2))

    # Format as native content
    native = formatter.format_as_native(
        ad_content,
        ContentContext.TOOL_LIMIT,
        user_context={"interests": ["analytics", "data science"]},
    )
    print(f"\nNative content: {native.headline}")
    print(f"Format: {native.format_type.value}")
    print(f"Reward preview: {native.reward_preview}")
