#!/usr/bin/env python3
"""
LUKHAS AI Platform API Integrations
Live deployment system for social media platforms with OAuth, rate limiting, and error handling
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import aiohttp

# Platform-specific imports
try:
    import tweepy  # Twitter API v2
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    import praw  # Reddit API
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

try:
    from linkedin_api import Linkedin  # LinkedIn API
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False

try:
    import requests_oauthlib  # OAuth for various platforms
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

@dataclass
class APICredentials:
    """API credentials for platform integration"""
    platform: str
    api_key: str
    api_secret: str
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    refresh_token: Optional[str] = None

@dataclass
class PostResult:
    """Result of posting to a platform"""
    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    response_data: Optional[dict] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None

@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    platform: str
    requests_remaining: int
    reset_time: datetime
    window_duration: int  # seconds
    last_request: datetime

class PlatformAPIManager:
    """
    Comprehensive API manager for all social media platforms
    Handles authentication, rate limiting, error handling, and posting
    """

    def __init__(self, credentials_path: str = None):
        self.base_path = Path(__file__).parent.parent
        self.credentials_path = credentials_path or (self.base_path / "config" / "api_credentials.json")
        self.logs_path = self.base_path / "logs"

        # Initialize components
        self.credentials: dict[str, APICredentials] = {}
        self.rate_limits: dict[str, RateLimitInfo] = {}
        self.platform_clients: dict[str, Any] = {}
        self.logger = self._setup_logging()

        # Load credentials and initialize clients
        self._load_credentials()
        self._initialize_platform_clients()

        # Rate limiting defaults (requests per hour)
        self.default_rate_limits = {
            "twitter": {"requests": 300, "window": 900},  # 300 per 15 minutes
            "linkedin": {"requests": 100, "window": 3600},  # 100 per hour
            "reddit": {"requests": 60, "window": 3600},   # 60 per hour
            "instagram": {"requests": 200, "window": 3600}, # 200 per hour
            "youtube": {"requests": 100, "window": 3600}   # 100 per hour
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup API integration logging"""
        logger = logging.getLogger("LUKHAS_Platform_APIs")
        logger.setLevel(logging.INFO)

        self.logs_path.mkdir(exist_ok=True)

        log_file = self.logs_path / f"platform_apis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_credentials(self):
        """Load API credentials from secure configuration"""

        # First try to load from file
        if self.credentials_path.exists():
            try:
                with open(self.credentials_path) as f:
                    creds_data = json.load(f)

                for platform, creds in creds_data.items():
                    self.credentials[platform] = APICredentials(**creds)

                self.logger.info(f"Loaded credentials for {len(self.credentials)} platforms")
            except Exception as e:
                self.logger.error(f"Failed to load credentials from file: {e}")

        # Then try to load from environment variables
        env_platforms = {
            "twitter": {
                "api_key": "TWITTER_API_KEY",
                "api_secret": "TWITTER_API_SECRET",
                "access_token": "TWITTER_ACCESS_TOKEN",
                "access_token_secret": "TWITTER_ACCESS_TOKEN_SECRET",
                "bearer_token": "TWITTER_BEARER_TOKEN"
            },
            "linkedin": {
                "client_id": "LINKEDIN_CLIENT_ID",
                "client_secret": "LINKEDIN_CLIENT_SECRET",
                "access_token": "LINKEDIN_ACCESS_TOKEN"
            },
            "reddit": {
                "client_id": "REDDIT_CLIENT_ID",
                "client_secret": "REDDIT_CLIENT_SECRET",
                "username": "REDDIT_USERNAME",
                "password": "REDDIT_PASSWORD"
            },
            "instagram": {
                "access_token": "INSTAGRAM_ACCESS_TOKEN",
                "client_id": "INSTAGRAM_CLIENT_ID",
                "client_secret": "INSTAGRAM_CLIENT_SECRET"
            }
        }

        for platform, env_vars in env_platforms.items():
            creds = {"platform": platform}

            for cred_key, env_key in env_vars.items():
                value = os.getenv(env_key)
                if value:
                    creds[cred_key] = value

            # Only create credentials if we have the minimum required
            if self._validate_credentials(platform, creds):
                self.credentials[platform] = APICredentials(**creds)
                self.logger.info(f"Loaded {platform} credentials from environment")

    def _validate_credentials(self, platform: str, creds: dict[str, str]) -> bool:
        """Validate that we have minimum required credentials for a platform"""

        required_fields = {
            "twitter": ["api_key", "api_secret"],
            "linkedin": ["client_id", "client_secret"],
            "reddit": ["client_id", "client_secret"],
            "instagram": ["access_token"]
        }

        if platform not in required_fields:
            return False

        for field in required_fields[platform]:
            if field not in creds or not creds[field]:
                return False

        return True

    def _initialize_platform_clients(self):
        """Initialize platform-specific API clients"""

        # Twitter/𝕏 API v2
        if "twitter" in self.credentials and TWITTER_AVAILABLE:
            try:
                creds = self.credentials["twitter"]

                # Initialize with bearer token for app-only auth if available
                if creds.bearer_token:
                    self.platform_clients["twitter"] = tweepy.Client(
                        bearer_token=creds.bearer_token,
                        consumer_key=creds.api_key,
                        consumer_secret=creds.api_secret,
                        access_token=creds.access_token,
                        access_token_secret=creds.access_token_secret,
                        wait_on_rate_limit=True
                    )
                else:
                    # Initialize with OAuth 1.0a
                    self.platform_clients["twitter"] = tweepy.Client(
                        consumer_key=creds.api_key,
                        consumer_secret=creds.api_secret,
                        access_token=creds.access_token,
                        access_token_secret=creds.access_token_secret,
                        wait_on_rate_limit=True
                    )

                self.logger.info("✅ Twitter API client initialized")

            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Twitter client: {e}")

        # Reddit API
        if "reddit" in self.credentials and REDDIT_AVAILABLE:
            try:
                creds = self.credentials["reddit"]

                self.platform_clients["reddit"] = praw.Reddit(
                    client_id=creds.client_id,
                    client_secret=creds.client_secret,
                    username=creds.username,
                    password=creds.password,
                    user_agent="LUKHAS AI Social Media Bot v1.0"
                )

                self.logger.info("✅ Reddit API client initialized")

            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Reddit client: {e}")

        # LinkedIn API (custom implementation)
        if "linkedin" in self.credentials:
            self.logger.info("✅ LinkedIn API credentials loaded (custom implementation)")

        # Instagram API (custom implementation)
        if "instagram" in self.credentials:
            self.logger.info("✅ Instagram API credentials loaded (custom implementation)")

    async def post_to_twitter(self, content: str, media_paths: list[str] = None) -> PostResult:
        """Post to Twitter/𝕏 using API v2"""

        if "twitter" not in self.platform_clients:
            return PostResult(
                success=False,
                platform="twitter",
                error="Twitter client not initialized"
            )

        try:
            client = self.platform_clients["twitter"]

            # Check rate limits
            if not await self._check_rate_limit("twitter"):
                return PostResult(
                    success=False,
                    platform="twitter",
                    error="Rate limit exceeded"
                )

            # Upload media if provided
            media_ids = []
            if media_paths:
                # Note: Media upload requires API v1.1 for now
                auth = tweepy.OAuth1UserHandler(
                    self.credentials["twitter"].api_key,
                    self.credentials["twitter"].api_secret,
                    self.credentials["twitter"].access_token,
                    self.credentials["twitter"].access_token_secret
                )
                api_v1 = tweepy.API(auth)

                for media_path in media_paths:
                    if Path(media_path).exists():
                        media = api_v1.media_upload(media_path)
                        media_ids.append(media.media_id)

            # Post tweet
            response = client.create_tweet(
                text=content,
                media_ids=media_ids if media_ids else None
            )

            # Update rate limit tracking
            await self._update_rate_limit("twitter")

            # Extract tweet URL
            tweet_id = response.data['id']
            username = client.get_me().data.username
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            self.logger.info(f"✅ Posted to Twitter: {tweet_url}")

            return PostResult(
                success=True,
                platform="twitter",
                post_id=tweet_id,
                url=tweet_url,
                response_data=response.data
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to post to Twitter: {e}")
            return PostResult(
                success=False,
                platform="twitter",
                error=str(e)
            )

    async def post_to_linkedin(self, content: str, media_paths: list[str] = None) -> PostResult:
        """Post to LinkedIn using custom API implementation"""

        if "linkedin" not in self.credentials:
            return PostResult(
                success=False,
                platform="linkedin",
                error="LinkedIn credentials not configured"
            )

        try:
            creds = self.credentials["linkedin"]

            # Check rate limits
            if not await self._check_rate_limit("linkedin"):
                return PostResult(
                    success=False,
                    platform="linkedin",
                    error="Rate limit exceeded"
                )

            # LinkedIn API requires OAuth 2.0 flow
            headers = {
                "Authorization": f"Bearer {creds.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get user profile to get person URN
            async with aiohttp.ClientSession() as session:
                # Get profile
                profile_url = "https://api.linkedin.com/v2/people/~"
                async with session.get(profile_url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to get LinkedIn profile: {response.status}")

                    profile_data = await response.json()
                    person_urn = profile_data["id"]

                # Create post
                post_data = {
                    "author": f"urn:li:person:{person_urn}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }

                # Post to LinkedIn
                post_url = "https://api.linkedin.com/v2/ugcPosts"
                async with session.post(post_url, headers=headers, json=post_data) as response:
                    if response.status == 201:
                        response_data = await response.json()
                        post_id = response_data.get("id")

                        # Update rate limit tracking
                        await self._update_rate_limit("linkedin")

                        self.logger.info(f"✅ Posted to LinkedIn: {post_id}")

                        return PostResult(
                            success=True,
                            platform="linkedin",
                            post_id=post_id,
                            response_data=response_data
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"LinkedIn API error {response.status}: {error_text}")

        except Exception as e:
            self.logger.error(f"❌ Failed to post to LinkedIn: {e}")
            return PostResult(
                success=False,
                platform="linkedin",
                error=str(e)
            )

    async def post_to_reddit(self, title: str, content: str, subreddit: str = "test") -> PostResult:
        """Post to Reddit using PRAW"""

        if "reddit" not in self.platform_clients:
            return PostResult(
                success=False,
                platform="reddit",
                error="Reddit client not initialized"
            )

        try:
            reddit = self.platform_clients["reddit"]

            # Check rate limits
            if not await self._check_rate_limit("reddit"):
                return PostResult(
                    success=False,
                    platform="reddit",
                    error="Rate limit exceeded"
                )

            # Submit post
            subreddit_obj = reddit.subreddit(subreddit)
            submission = subreddit_obj.submit(title=title, selftext=content)

            # Update rate limit tracking
            await self._update_rate_limit("reddit")

            post_url = f"https://reddit.com{submission.permalink}"

            self.logger.info(f"✅ Posted to Reddit r/{subreddit}: {post_url}")

            return PostResult(
                success=True,
                platform="reddit",
                post_id=submission.id,
                url=post_url,
                response_data={"subreddit": subreddit, "title": title}
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to post to Reddit: {e}")
            return PostResult(
                success=False,
                platform="reddit",
                error=str(e)
            )

    async def post_to_instagram(self, content: str, media_path: str) -> PostResult:
        """Post to Instagram using Graph API"""

        if "instagram" not in self.credentials:
            return PostResult(
                success=False,
                platform="instagram",
                error="Instagram credentials not configured"
            )

        try:
            self.credentials["instagram"]

            # Check rate limits
            if not await self._check_rate_limit("instagram"):
                return PostResult(
                    success=False,
                    platform="instagram",
                    error="Rate limit exceeded"
                )

            # Instagram requires image upload via Graph API
            # This is a simplified version - full implementation would handle
            # image uploads, video uploads, and carousel posts

            async with aiohttp.ClientSession():
                # For now, return a placeholder implementation
                # Real implementation would:
                # 1. Upload media to Instagram servers
                # 2. Create media container with caption
                # 3. Publish the container

                self.logger.warning("Instagram posting is placeholder - requires Graph API setup")

                return PostResult(
                    success=False,
                    platform="instagram",
                    error="Instagram API implementation pending - requires Facebook Graph API setup"
                )

        except Exception as e:
            self.logger.error(f"❌ Failed to post to Instagram: {e}")
            return PostResult(
                success=False,
                platform="instagram",
                error=str(e)
            )

    async def _check_rate_limit(self, platform: str) -> bool:
        """Check if we can make a request within rate limits"""

        if platform not in self.rate_limits:
            # Initialize rate limit tracking
            self.rate_limits[platform] = RateLimitInfo(
                platform=platform,
                requests_remaining=self.default_rate_limits[platform]["requests"],
                reset_time=datetime.now() + timedelta(seconds=self.default_rate_limits[platform]["window"]),
                window_duration=self.default_rate_limits[platform]["window"],
                last_request=datetime.now() - timedelta(hours=1)
            )

        rate_limit = self.rate_limits[platform]
        now = datetime.now()

        # Reset if window has passed
        if now >= rate_limit.reset_time:
            rate_limit.requests_remaining = self.default_rate_limits[platform]["requests"]
            rate_limit.reset_time = now + timedelta(seconds=rate_limit.window_duration)

        # Check if we have requests remaining
        if rate_limit.requests_remaining <= 0:
            self.logger.warning(f"Rate limit exceeded for {platform}. Reset at {rate_limit.reset_time}")
            return False

        return True

    async def _update_rate_limit(self, platform: str):
        """Update rate limit tracking after making a request"""

        if platform in self.rate_limits:
            self.rate_limits[platform].requests_remaining -= 1
            self.rate_limits[platform].last_request = datetime.now()

    def get_platform_status(self) -> dict[str, Any]:
        """Get status of all platform integrations"""

        status = {}

        for platform in ["twitter", "linkedin", "reddit", "instagram"]:
            platform_status = {
                "credentials_configured": platform in self.credentials,
                "client_initialized": platform in self.platform_clients,
                "library_available": self._check_library_availability(platform),
                "rate_limit_status": None
            }

            if platform in self.rate_limits:
                rate_limit = self.rate_limits[platform]
                platform_status["rate_limit_status"] = {
                    "requests_remaining": rate_limit.requests_remaining,
                    "reset_time": rate_limit.reset_time.isoformat(),
                    "last_request": rate_limit.last_request.isoformat()
                }

            status[platform] = platform_status

        return status

    def _check_library_availability(self, platform: str) -> bool:
        """Check if required libraries are available for a platform"""

        availability = {
            "twitter": TWITTER_AVAILABLE,
            "reddit": REDDIT_AVAILABLE,
            "linkedin": OAUTH_AVAILABLE,  # Custom implementation with OAuth
            "instagram": OAUTH_AVAILABLE  # Custom implementation with OAuth
        }

        return availability.get(platform, False)

    async def post_content(self, platform: str, content: str, title: str = None,
                          media_paths: list[str] = None, **kwargs) -> PostResult:
        """Universal posting method for any platform"""

        self.logger.info(f"📤 Posting to {platform}: {title or content[:50]}...")

        try:
            if platform == "twitter":
                return await self.post_to_twitter(content, media_paths)

            elif platform == "linkedin":
                return await self.post_to_linkedin(content, media_paths)

            elif platform == "reddit":
                subreddit = kwargs.get("subreddit", "test")
                return await self.post_to_reddit(title or "LUKHAS AI Update", content, subreddit)

            elif platform == "instagram":
                if media_paths and len(media_paths) > 0:
                    return await self.post_to_instagram(content, media_paths[0])
                else:
                    return PostResult(
                        success=False,
                        platform="instagram",
                        error="Instagram requires media"
                    )

            else:
                return PostResult(
                    success=False,
                    platform=platform,
                    error=f"Platform {platform} not supported"
                )

        except Exception as e:
            self.logger.error(f"❌ Failed to post to {platform}: {e}")
            return PostResult(
                success=False,
                platform=platform,
                error=str(e)
            )

# Global API manager instance
api_manager: Optional[PlatformAPIManager] = None

def get_api_manager() -> PlatformAPIManager:
    """Get or create the global API manager"""
    global api_manager

    if api_manager is None:
        api_manager = PlatformAPIManager()

    return api_manager

# Example usage and testing
async def main():
    """Test the platform API integrations"""

    manager = get_api_manager()

    print("🔌 LUKHAS AI Platform API Integrations")
    print("=" * 60)

    # Check platform status
    status = manager.get_platform_status()
    print("\n📊 Platform Status:")
    for platform, info in status.items():
        credentials = "✅" if info["credentials_configured"] else "❌"
        client = "✅" if info["client_initialized"] else "❌"
        library = "✅" if info["library_available"] else "❌"

        print(f"   {platform.title()}: Creds {credentials} | Client {client} | Library {library}")

    # Test posting (only if credentials are available)
    test_content = "🧠 Testing LUKHAS AI consciousness technology platform integration! The Trinity Framework (⚛️🧠🛡️) ensures our AI systems maintain authentic, aware, and ethical operation. What aspects of conscious AI development interest you most? #ConsciousnessTechnology #LUKHASIA"

    for platform in ["twitter", "linkedin", "reddit"]:
        if status[platform]["credentials_configured"] and status[platform]["client_initialized"]:
            print(f"\n🧪 Testing {platform} posting...")

            result = await manager.post_content(
                platform=platform,
                content=test_content,
                title="LUKHAS AI Platform Integration Test",
                subreddit="test" if platform == "reddit" else None
            )

            if result.success:
                print(f"✅ {platform} posting successful: {result.url or result.post_id}")
            else:
                print(f"❌ {platform} posting failed: {result.error}")
        else:
            print(f"⚠️ {platform} not configured for testing")

    print("\n⚛️🧠🛡️ LUKHAS AI Platform Integration Test Complete")

if __name__ == "__main__":
    asyncio.run(main())
