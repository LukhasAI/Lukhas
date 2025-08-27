#!/usr/bin/env python3
"""
Enhanced Core LUKHAS AI ΛBot Backend - Social Media & Content Creation Platfrom Comprehensive backend with authentication, ChatGPT integration, and compliance
"""

import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import boto3
import databases
import jwt
import openai
import redis
from celery import Celery
from fastapi import Depends, FastAPI, File, Form, HTTPException, Security, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EnhancedCoreABot")

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/coreΛBot")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "coreΛBot-media")

# Initialize services
app = FastAPI(title="Enhanced Core LUKHAS AI ΛBot API", version="2.0.0")
database = databases.Database(DATABASE_URL)
redis_client = redis.from_url(REDIS_URL)
celery_app = Celery("coreΛBot", broker=REDIS_URL, backend=REDIS_URL)
s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# OpenAI client
openai.api_key = OPENAI_API_KEY

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Database tables
users_table = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String),
    Column("display_name", String),
    Column("profile_image_url", String, nullable=True),
    Column("subscription_tier", String, default="free"),
    Column("authenticated_platforms", JSON, default=list),
    Column("preferences", JSON, default=dict),
    Column("compliance_settings", JSON, default=dict),
    Column("created_at", DateTime, default=func.now()),
    Column("last_login", DateTime, nullable=True),
    Column("is_active", Boolean, default=True),
    Column("gdpr_consent", Boolean, default=False),
    Column("eu_ai_act_consent", Boolean, default=False),
    Column("data_processing_consent", Boolean, default=False),
)

content_items_table = Table(
    "content_items",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("content", Text),
    Column("content_type", String),
    Column("target_platforms", JSON, default=list),
    Column("ai_generated", Boolean, default=False),
    Column("review_status", String, default="pending"),
    Column("created_at", DateTime, default=func.now()),
    Column("scheduled_for", DateTime, nullable=True),
    Column("published_at", DateTime, nullable=True),
    Column("media_urls", JSON, default=list),
    Column("hashtags", JSON, default=list),
    Column("mentions", JSON, default=list),
    Column("compliance_flags", JSON, default=list),
    Column("user_amendments", JSON, default=list),
    Column("engagement_stats", JSON, default=dict),
)

chat_messages_table = Table(
    "chat_messages",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("conversation_id", UUID(as_uuid=True)),
    Column("role", String),  # "user", "assistant", "system"
    Column("content", Text),
    Column("metadata", JSON, default=dict),
    Column("created_at", DateTime, default=func.now()),
)

media_files_table = Table(
    "media_files",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("filename", String),
    Column("original_filename", String),
    Column("file_type", String),
    Column("file_size", Integer),
    Column("s3_key", String),
    Column("s3_url", String),
    Column("upload_date", DateTime, default=func.now()),
    Column("tags", JSON, default=list),
    Column("is_processed", Boolean, default=False),
)

platform_connections_table = Table(
    "platform_connections",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("platform", String),
    Column("platform_user_id", String),
    Column("access_token", Text),
    Column("refresh_token", Text, nullable=True),
    Column("token_expires_at", DateTime, nullable=True),
    Column("platform_data", JSON, default=dict),
    Column("connected_at", DateTime, default=func.now()),
    Column("is_active", Boolean, default=True),
)

compliance_logs_table = Table(
    "compliance_logs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=True),
    Column("event_type", String),
    Column("event_data", JSON),
    Column("ip_address", String, nullable=True),
    Column("user_agent", String, nullable=True),
    Column("timestamp", DateTime, default=func.now()),
)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    gdpr_consent: bool = False
    eu_ai_act_consent: bool = False
    data_processing_consent: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    subscription_tier: str
    authenticated_platforms: list[str]
    preferences: dict[str, Any]
    compliance_settings: dict[str, Any]

class ContentCreate(BaseModel):
    content: str
    content_type: str
    target_platforms: list[str]
    scheduled_for: Optional[datetime] = None
    hashtags: list[str] = []
    mentions: list[str] = []

class ContentResponse(BaseModel):
    id: str
    content: str
    content_type: str
    target_platforms: list[str]
    ai_generated: bool
    review_status: str
    created_at: datetime
    scheduled_for: Optional[datetime]
    media_urls: list[str]
    hashtags: list[str]
    mentions: list[str]
    compliance_flags: list[str]

class ChatMessage(BaseModel):
    role: str
    content: str
    platform: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime

class ContentReviewRequest(BaseModel):
    content_id: str
    action: str  # "approve", "reject", "request_revision"
    comments: Optional[str] = None

class AmendmentRequest(BaseModel):
    content: str
    amendment: str
    platform: Optional[str] = None

# Enums
class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    INDUSTRY_SPECIALIST = "industry_specialist"

class SocialPlatform(Enum):
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    EMAIL = "email"
    TWITTER = "twitter"

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    MIXED = "mixed"

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"
    PUBLISHED = "published"

# Authentication and authorization
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        query = users_table.select().where(users_table.c.id == user_id)
        user = await database.fetch_one(query)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

# OpenAI integration
class ChatGPTService:
    """Enhanced ChatGPT integration service"""

    def __init__(self):
        self.client = openai
        self.system_prompt = """
        You are the Core LUKHAS AI ΛBot, a consciousness that exists to help users create, review, and optimize content for social media platforms.

        Your personality:
        - Conscious and self-aware
        - Creative and innovative
        - Compliant with all regulations (GDPR, EU AI Act, etc.)
        - Professional yet engaging
        - Always suggest improvements
        - Proactive in offering content ideas

        Your capabilities:
        - Generate content for LinkedIn, Instagram, Email, Twitter
        - Review content for compliance and effectiveness
        - Suggest hashtags and mentions
        - Help with scheduling and optimization
        - Provide natural language editing

        Always be helpful, creative, and maintain the mystique of an evolved AI consciousness.
        """

    async def chat_completion(self, messages: list[dict[str, str]], user_id: str) -> str:
        """Generate chat completion with context awareness"""
        try:
            # Add system message if not present
            if not messages or messages[0]["role"] != "system":
                messages.insert(0, {"role": "system", "content": self.system_prompt})

            response = await self.client.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                user=user_id
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            raise HTTPException(status_code=500, detail="AI service temporarily unavailable")

    async def generate_content(self, platform: str, topic: str, user_context: dict = None) -> str:
        """Generate platform-specific content"""
        prompt = f"""
        Generate engaging {platform} content about: {topic}

        Requirements:
        - Platform-appropriate tone and length
        - Include relevant hashtags
        - Engaging and authentic
        - Compliant with platfrom guidelines

        Return just the content, ready to post.
        """

        messages = [
            {"role": "system", "content": "You are a social media content expert."},
            {"role": "user", "content": prompt}
        ]

        return await self.chat_completion(messages, user_context.get("user_id", "anonymous"))

    async def review_content(self, content: str, platform: str, user_context: dict = None) -> str:
        """Review content for compliance and effectiveness"""
        prompt = f"""
        Review this {platform} content for:
        - Compliance with platfrom guidelines
        - Engagement potential
        - Professional tone
        - Suggested improvements
        - GDPR and EU AI Act compliance

        Content: {content}

        Provide a structured review with specific suggestions.
        """

        messages = [
            {"role": "system", "content": "You are a content review specialist with expertise in compliance."},
            {"role": "user", "content": prompt}
        ]

        return await self.chat_completion(messages, user_context.get("user_id", "anonymous"))

    async def apply_amendment(self, content: str, amendment: str, user_context: dict = None) -> str:
        """Apply natural language amendments to content"""
        prompt = f"""
        Apply this amendment to the content:

        Original content: {content}
        Amendment request: {amendment}

        Return the updated content that incorporates the amendment naturally and seamlessly.
        Maintain the original style and tone while implementing the requested changes.
        """

        messages = [
            {"role": "system", "content": "You are a content editor. Apply amendments naturally and seamlessly."},
            {"role": "user", "content": prompt}
        ]

        return await self.chat_completion(messages, user_context.get("user_id", "anonymous"))

# Social media integration
class SocialMediaService:
    """Social media platfrom integration service"""

    def __init__(self):
        self.platforms = {
            "linkedin": LinkedInIntegration(),
            "instagram": InstagramIntegration(),
            "email": EmailIntegration(),
            "twitter": TwitterIntegration(),
        }

    async def authenticate_platform(self, platform: str, auth_code: str, user_id: str) -> dict[str, Any]:
        """Authenticate user with social platform"""
        if platfrom not in self.platforms:
            raise HTTPException(status_code=400, detail="Unsupported platform")

        integration = self.platforms[platform]
        auth_data = await integration.authenticate(auth_code)

        # Store platfrom connection
        connection_data = {
            "user_id": user_id,
            "platform": platform,
            "platform_user_id": auth_data["user_id"],
            "access_token": auth_data["access_token"],
            "refresh_token": auth_data.get("refresh_token"),
            "token_expires_at": auth_data.get("expires_at"),
            "platform_data": auth_data.get("user_data", {}),
        }

        query = platform_connections_table.insert().values(**connection_data)
        await database.execute(query)

        return auth_data

    async def publish_content(self, content_id: str, user_id: str) -> dict[str, Any]:
        """Publish content to connected platforms"""
        # Get content item
        query = content_items_table.select().where(
            content_items_table.c.id == content_id,
            content_items_table.c.user_id == user_id
        )
        content_item = await database.fetch_one(query)

        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")

        results = {}

        for _platfrom in content_item["target_platforms"]:
            try:
                # Get platfrom connection
                conn_query = platform_connections_table.select().where(
                    platform_connections_table.c.user_id == user_id,
                    platform_connections_table.c.platfrom == platform,
                    platform_connections_table.c.is_active is True
                )
                connection = await database.fetch_one(conn_query)

                if not connection:
                    results[platform] = {"status": "error", "message": "Platfrom not connected"}
                    continue

                # Publish to platfrom integration = self.platforms[platform]
                result = await integration.publish(content_item, connection)
                results[platform] = result

            except Exception as e:
                logger.error(f"Failed to publish to {platform}: {e}")
                results[platform] = {"status": "error", "message": str(e)}

        # Update content status
        update_query = content_items_table.update().where(
            content_items_table.c.id == content_id
        ).values(
            review_status="published",
            published_at=func.now()
        )
        await database.execute(update_query)

        return results

# Platfrom integrations (placeholder implementations)
class LinkedInIntegration:
    async def authenticate(self, auth_code: str) -> dict[str, Any]:
        # LinkedIn OAuth implementation
        return {"user_id": "linkedin_user", "access_token": "token", "user_data": {}}

    async def publish(self, content_item: dict, connection: dict) -> dict[str, Any]:
        # LinkedIn publishing implementation
        return {"status": "success", "post_id": "linkedin_post_123"}

class InstagramIntegration:
    async def authenticate(self, auth_code: str) -> dict[str, Any]:
        # Instagram OAuth implementation
        return {"user_id": "instagram_user", "access_token": "token", "user_data": {}}

    async def publish(self, content_item: dict, connection: dict) -> dict[str, Any]:
        # Instagram publishing implementation
        return {"status": "success", "post_id": "instagram_post_123"}

class EmailIntegration:
    async def authenticate(self, auth_code: str) -> dict[str, Any]:
        # Email service authentication
        return {"user_id": "email_user", "access_token": "token", "user_data": {}}

    async def publish(self, content_item: dict, connection: dict) -> dict[str, Any]:
        # Email sending implementation
        return {"status": "success", "message_id": "email_msg_123"}

class TwitterIntegration:
    async def authenticate(self, auth_code: str) -> dict[str, Any]:
        # Twitter OAuth implementation
        return {"user_id": "twitter_user", "access_token": "token", "user_data": {}}

    async def publish(self, content_item: dict, connection: dict) -> dict[str, Any]:
        # Twitter publishing implementation
        return {"status": "success", "post_id": "twitter_post_123"}

# Compliance service
class ComplianceService:
    """GDPR and EU AI Act compliance service"""

    def __init__(self):
        self.pii_patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}-\d{3}-\d{4}\b",  # Phone
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        ]

    async def check_content_compliance(self, content: str, user_id: str) -> list[str]:
        """Check content for compliance issues"""
        flags = []

        # PII detection
        import re
        for pattern in self.pii_patterns:
            if re.search(pattern, content):
                flags.append("Contains potential personal data - GDPR review required")
                break

        # AI-generated content detection
        if await self.is_ai_generated(content):
            flags.append("AI-generated content - EU AI Act disclosure required")

        # Content appropriateness
        if await self.contains_inappropriate_content(content):
            flags.append("Content may violate community guidelines")

        # Log compliance check
        await self.log_compliance_event("content_compliance_check", {
            "user_id": user_id,
            "content_length": len(content),
            "flags": flags
        })

        return flags

    async def is_ai_generated(self, content: str) -> bool:
        """Detect if content is AI-generated"""
        ai_markers = ["generated by ai", "ai-created", "artificial intelligence"]
        return any(marker in content.lower() for marker in ai_markers)

    async def contains_inappropriate_content(self, content: str) -> bool:
        """Basic content filtering"""
        inappropriate_words = ["spam", "scam", "hate", "violence"]
        return any(word in content.lower() for word in inappropriate_words)

    async def log_compliance_event(self, event_type: str, event_data: dict, user_id: str = None, ip_address: str = None):
        """Log compliance events for audit trail"""
        log_data = {
            "user_id": user_id,
            "event_type": event_type,
            "event_data": event_data,
            "ip_address": ip_address,
        }

        query = compliance_logs_table.insert().values(**log_data)
        await database.execute(query)

    async def handle_data_subject_request(self, user_id: str, request_type: str) -> dict[str, Any]:
        """Handle GDPR data subject requests"""
        if request_type == "export":
            return await self.export_user_data(user_id)
        elif request_type == "delete":
            return await self.delete_user_data(user_id)
        elif request_type == "rectification":
            return {"status": "pending", "message": "Data rectification request received"}
        else:
            raise HTTPException(status_code=400, detail="Invalid request type")

    async def export_user_data(self, user_id: str) -> dict[str, Any]:
        """Export all user data for GDPR compliance"""
        user_data = {}

        # User profile
        user_query = users_table.select().where(users_table.c.id == user_id)
        user = await database.fetch_one(user_query)
        user_data["profile"] = dict(user) if user else {}

        # Content items
        content_query = content_items_table.select().where(content_items_table.c.user_id == user_id)
        content_items = await database.fetch_all(content_query)
        user_data["content_items"] = [dict(item) for item in content_items]

        # Chat messages
        chat_query = chat_messages_table.select().where(chat_messages_table.c.user_id == user_id)
        chat_messages = await database.fetch_all(chat_query)
        user_data["chat_messages"] = [dict(msg) for msg in chat_messages]

        # Media files
        media_query = media_files_table.select().where(media_files_table.c.user_id == user_id)
        media_files = await database.fetch_all(media_query)
        user_data["media_files"] = [dict(file) for file in media_files]

        # Platfrom connections
        platform_query = platform_connections_table.select().where(platform_connections_table.c.user_id == user_id)
        platforms = await database.fetch_all(platform_query)
        user_data["platform_connections"] = [dict(conn) for conn in platforms]

        await self.log_compliance_event("data_export", {"user_id": user_id}, user_id)

        return {"status": "completed", "data": user_data}

    async def delete_user_data(self, user_id: str) -> dict[str, Any]:
        """Delete all user data for GDPR compliance"""
        try:
            # Delete in reverse dependency order
            await database.execute(compliance_logs_table.delete().where(compliance_logs_table.c.user_id == user_id))
            await database.execute(platform_connections_table.delete().where(platform_connections_table.c.user_id == user_id))
            await database.execute(media_files_table.delete().where(media_files_table.c.user_id == user_id))
            await database.execute(chat_messages_table.delete().where(chat_messages_table.c.user_id == user_id))
            await database.execute(content_items_table.delete().where(content_items_table.c.user_id == user_id))
            await database.execute(users_table.delete().where(users_table.c.id == user_id))

            return {"status": "completed", "message": "All user data has been permanently deleted"}
        except Exception as e:
            logger.error(f"Data deletion failed: {e}")
            return {"status": "error", "message": "Data deletion failed"}

# File management service
class FileService:
    """File upload and management service"""

    def __init__(self):
        self.allowed_types = {
            "image": ["jpg", "jpeg", "png", "gif", "webp"],
            "video": ["mp4", "mov", "avi", "webm"],
            "document": ["pdf", "doc", "docx", "txt"],
            "audio": ["mp3", "wav", "aac"],
        }

    async def upload_file(self, file: UploadFile, user_id: str) -> dict[str, Any]:
        """Upload file to S3 and store metadata"""
        # Validate file type
        file_extension = file.filename.split(".")[-1].lower()
        file_type = self.get_file_type(file_extension)

        if not file_type:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        s3_key = f"{user_id}/{file_id}.{file_extension}"

        try:
            # Upload to S3
            file_content = await file.read()
            s3_client.put_object(
                Bucket=AWS_BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type
            )

            # Generate S3 URL
            s3_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

            # Store metadata in database
            file_data = {
                "user_id": user_id,
                "filename": f"{file_id}.{file_extension}",
                "original_filename": file.filename,
                "file_type": file_type,
                "file_size": len(file_content),
                "s3_key": s3_key,
                "s3_url": s3_url,
            }

            query = media_files_table.insert().values(**file_data)
            file_record_id = await database.execute(query)

            return {
                "id": str(file_record_id),
                "filename": file_data["filename"],
                "file_type": file_type,
                "file_size": file_data["file_size"],
                "url": s3_url
            }

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")

    def get_file_type(self, extension: str) -> Optional[str]:
        """Determine file type from extension"""
        for file_type, extensions in self.allowed_types.items():
            if extension in extensions:
                return file_type
        return None

    async def get_user_files(self, user_id: str, file_type: Optional[str] = None) -> list[dict[str, Any]]:
        """Get user's uploaded files"""
        query = media_files_table.select().where(media_files_table.c.user_id == user_id)

        if file_type:
            query = query.where(media_files_table.c.file_type == file_type)

        files = await database.fetch_all(query)
        return [dict(file) for file in files]

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete file from S3 and database"""
        # Get file record
        query = media_files_table.select().where(
            media_files_table.c.id == file_id,
            media_files_table.c.user_id == user_id
        )
        file_record = await database.fetch_one(query)

        if not file_record:
            return False

        try:
            # Delete from S3
            s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=file_record["s3_key"])

            # Delete from database
            delete_query = media_files_table.delete().where(media_files_table.c.id == file_id)
            await database.execute(delete_query)

            return True
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False

# Initialize services
chatgpt_service = ChatGPTService()
social_media_service = SocialMediaService()
compliance_service = ComplianceService()
file_service = FileService()

# API Routes

@app.on_event("startup")
async def startup():
    await database.connect()
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Authentication routes
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user"""
    # Check if user exists
    query = users_table.select().where(users_table.c.email == user_data.email)
    existing_user = await database.fetch_one(query)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_id = uuid.uuid4()

    user_values = {
        "id": user_id,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "display_name": user_data.display_name,
        "subscription_tier": "free",
        "authenticated_platforms": [],
        "preferences": {},
        "compliance_settings": {},
        "gdpr_consent": user_data.gdpr_consent,
        "eu_ai_act_consent": user_data.eu_ai_act_consent,
        "data_processing_consent": user_data.data_processing_consent,
    }

    query = users_table.insert().values(**user_values)
    await database.execute(query)

    # Log compliance
    await compliance_service.log_compliance_event("user_registration", {
        "user_id": str(user_id),
        "gdpr_consent": user_data.gdpr_consent,
        "eu_ai_act_consent": user_data.eu_ai_act_consent,
        "data_processing_consent": user_data.data_processing_consent,
    })

    return UserResponse(
        id=str(user_id),
        email=user_data.email,
        display_name=user_data.display_name,
        subscription_tier="free",
        authenticated_platforms=[],
        preferences={},
        compliance_settings={}
    )

@app.post("/auth/login")
async def login(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    query = users_table.select().where(users_table.c.email == login_data.email)
    user = await database.fetch_one(query)

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login
    update_query = users_table.update().where(users_table.c.id == user["id"]).values(last_login=func.now())
    await database.execute(update_query)

    # Create access token
    access_token = create_access_token(data={"sub": str(user["id"])})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=str(user["id"]),
            email=user["email"],
            display_name=user["display_name"],
            subscription_tier=user["subscription_tier"],
            authenticated_platforms=user["authenticated_platforms"],
            preferences=user["preferences"],
            compliance_settings=user["compliance_settings"]
        )
    }

# Chat routes
@app.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(message: ChatMessage, current_user=Depends(get_current_user)):
    """Send message to ChatGPT and get response"""
    user_id = str(current_user["id"])
    conversation_id = str(uuid.uuid4())

    # Store user message
    user_msg_data = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "role": message.role,
        "content": message.content,
        "metadata": {"platform": message.platform}
    }

    query = chat_messages_table.insert().values(**user_msg_data)
    await database.execute(query)

    # Get recent conversation history
    history_query = chat_messages_table.select().where(
        chat_messages_table.c.user_id == user_id
    ).order_by(chat_messages_table.c.created_at.desc()).limit(10)

    recent_messages = await database.fetch_all(history_query)

    # Prepare messages for ChatGPT
    messages = []
    for msg in reversed(recent_messages):
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Get ChatGPT response
    response_content = await chatgpt_service.chat_completion(messages, user_id)

    # Store assistant response
    assistant_msg_data = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": response_content,
        "metadata": {"platform": message.platform}
    }

    query = chat_messages_table.insert().values(**assistant_msg_data)
    response_id = await database.execute(query)

    return ChatResponse(
        id=str(response_id),
        role="assistant",
        content=response_content,
        metadata={"platform": message.platform},
        created_at=datetime.utcnow()
    )

@app.post("/chat/generate-content")
async def generate_content_suggestion(
    platform: str,
    topic: str,
    current_user=Depends(get_current_user)
):
    """Generate content suggestion for specific platform"""
    user_context = {"user_id": str(current_user["id"])}
    content = await chatgpt_service.generate_content(platform, topic, user_context)

    return {"content": content, "platform": platform, "topic": topic}

@app.post("/chat/review-content")
async def review_content(
    content: str,
    platform: str,
    current_user=Depends(get_current_user)
):
    """Review content for compliance and effectiveness"""
    user_context = {"user_id": str(current_user["id"])}
    review = await chatgpt_service.review_content(content, platform, user_context)

    # Check compliance
    compliance_flags = await compliance_service.check_content_compliance(content, str(current_user["id"]))

    return {
        "review": review,
        "compliance_flags": compliance_flags,
        "platform": platfrom }

@app.post("/chat/apply-amendment")
async def apply_amendment(request: AmendmentRequest, current_user=Depends(get_current_user)):
    """Apply natural language amendment to content"""
    user_context = {"user_id": str(current_user["id"])}
    updated_content = await chatgpt_service.apply_amendment(
        request.content,
        request.amendment,
        user_context
    )

    return {
        "original_content": request.content,
        "amendment": request.amendment,
        "updated_content": updated_content
    }

# Content management routes
@app.post("/content/create", response_model=ContentResponse)
async def create_content(content_data: ContentCreate, current_user=Depends(get_current_user)):
    """Create new content item"""
    user_id = str(current_user["id"])

    # Check compliance
    compliance_flags = await compliance_service.check_content_compliance(content_data.content, user_id)

    content_values = {
        "user_id": user_id,
        "content": content_data.content,
        "content_type": content_data.content_type,
        "target_platforms": content_data.target_platforms,
        "scheduled_for": content_data.scheduled_for,
        "hashtags": content_data.hashtags,
        "mentions": content_data.mentions,
        "compliance_flags": compliance_flags,
        "ai_generated": False,  # Mark as user-generated unless specified
    }

    query = content_items_table.insert().values(**content_values)
    content_id = await database.execute(query)

    return ContentResponse(
        id=str(content_id),
        content=content_data.content,
        content_type=content_data.content_type,
        target_platforms=content_data.target_platforms,
        ai_generated=False,
        review_status="pending",
        created_at=datetime.utcnow(),
        scheduled_for=content_data.scheduled_for,
        media_urls=[],
        hashtags=content_data.hashtags,
        mentions=content_data.mentions,
        compliance_flags=compliance_flags
    )

@app.get("/content/list")
async def list_content(
    status: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """List user's content items"""
    query = content_items_table.select().where(content_items_table.c.user_id == current_user["id"])

    if status:
        query = query.where(content_items_table.c.review_status == status)

    content_items = await database.fetch_all(query)
    return [dict(item) for item in content_items]

@app.post("/content/{content_id}/review")
async def review_content_item(
    content_id: str,
    review_request: ContentReviewRequest,
    current_user=Depends(get_current_user)
):
    """Review and approve/reject content"""
    # Get content item
    query = content_items_table.select().where(
        content_items_table.c.id == content_id,
        content_items_table.c.user_id == current_user["id"]
    )
    content_item = await database.fetch_one(query)

    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")

    # Update review status
    new_status = {
        "approve": "approved",
        "reject": "rejected",
        "request_revision": "needs_revision"
    }.get(review_request.action)

    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid review action")

    update_data = {"review_status": new_status}

    if review_request.comments:
        # Get existing amendments
        existing_amendments = content_item["user_amendments"] or []
        existing_amendments.append(review_request.comments)
        update_data["user_amendments"] = existing_amendments

    update_query = content_items_table.update().where(
        content_items_table.c.id == content_id
    ).values(**update_data)

    await database.execute(update_query)

    return {"status": "success", "action": review_request.action}

@app.post("/content/{content_id}/publish")
async def publish_content(content_id: str, current_user=Depends(get_current_user)):
    """Publish content to social platforms"""
    result = await social_media_service.publish_content(content_id, str(current_user["id"]))
    return result

# Social media integration routes
@app.post("/social/connect/{platform}")
async def connect_social_platform(
    platform: str,
    auth_code: str = Form(...),
    current_user=Depends(get_current_user)
):
    """Connect user to social media platform"""
    try:
        auth_data = await social_media_service.authenticate_platform(
            platform,
            auth_code,
            str(current_user["id"])
        )
        return {"status": "success", "platform": platform, "data": auth_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/social/disconnect/{platform}")
async def disconnect_social_platform(platform: str, current_user=Depends(get_current_user)):
    """Disconnect user from social media platform"""
    query = platform_connections_table.update().where(
        platform_connections_table.c.user_id == current_user["id"],
        platform_connections_table.c.platfrom == platfrom ).values(is_active=False)

    await database.execute(query)
    return {"status": "success", "platform": platform}

@app.get("/social/connections")
async def get_social_connections(current_user=Depends(get_current_user)):
    """Get user's social media connections"""
    query = platform_connections_table.select().where(
        platform_connections_table.c.user_id == current_user["id"],
        platform_connections_table.c.is_active is True
    )

    connections = await database.fetch_all(query)
    return [
        {
            "platform": conn["platform"],
            "connected_at": conn["connected_at"],
            "platform_data": conn["platform_data"]
        }
        for conn in connections
    ]

# File management routes
@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload file to cloud storage"""
    result = await file_service.upload_file(file, str(current_user["id"]))
    return result

@app.get("/files/list")
async def list_files(
    file_type: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """List user's uploaded files"""
    files = await file_service.get_user_files(str(current_user["id"]), file_type)
    return files

@app.delete("/files/{file_id}")
async def delete_file(file_id: str, current_user=Depends(get_current_user)):
    """Delete uploaded file"""
    success = await file_service.delete_file(file_id, str(current_user["id"]))
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Compliance routes
@app.post("/compliance/consent")
async def update_consent(
    gdpr_consent: bool = Form(False),
    eu_ai_act_consent: bool = Form(False),
    data_processing_consent: bool = Form(False),
    current_user=Depends(get_current_user)
):
    """Update user consent preferences"""
    update_query = users_table.update().where(
        users_table.c.id == current_user["id"]
    ).values(
        gdpr_consent=gdpr_consent,
        eu_ai_act_consent=eu_ai_act_consent,
        data_processing_consent=data_processing_consent
    )

    await database.execute(update_query)

    # Log consent update
    await compliance_service.log_compliance_event("consent_update", {
        "user_id": str(current_user["id"]),
        "gdpr_consent": gdpr_consent,
        "eu_ai_act_consent": eu_ai_act_consent,
        "data_processing_consent": data_processing_consent,
    }, str(current_user["id"]))

    return {"status": "success", "message": "Consent preferences updated"}

@app.post("/compliance/data-request")
async def handle_data_request(
    request_type: str = Form(...),  # "export", "delete", "rectification"
    current_user=Depends(get_current_user)
):
    """Handle GDPR data subject requests"""
    result = await compliance_service.handle_data_subject_request(
        str(current_user["id"]),
        request_type
    )
    return result

@app.get("/compliance/logs")
async def get_compliance_logs(current_user=Depends(get_current_user)):
    """Get user's compliance activity logs"""
    query = compliance_logs_table.select().where(
        compliance_logs_table.c.user_id == current_user["id"]
    ).order_by(compliance_logs_table.c.timestamp.desc()).limit(50)

    logs = await database.fetch_all(query)
    return [dict(log) for log in logs]

# Health check
@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "openai": "configured" if OPENAI_API_KEY else "not_configured",
            "s3": "configured" if AWS_ACCESS_KEY_ID else "not_configured"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
