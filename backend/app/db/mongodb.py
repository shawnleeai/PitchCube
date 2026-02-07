"""
MongoDB database connection
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings
from app.core.logging import logger


class MongoDB:
    """MongoDB connection manager."""

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database = None
        self.connected = False

    async def connect(self):
        """Connect to MongoDB."""
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=45000,
                serverSelectionTimeoutMS=5000,  # 减少等待时间
            )

            # Verify connection
            await self.client.admin.command("ping")

            self.database = self.client[settings.MONGODB_DB_NAME]

            # Create indexes
            await self._create_indexes()

            self.connected = True
            logger.info("MongoDB connection established successfully")

        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            logger.warning(f"MongoDB unavailable, running in demo mode: {e}")
            self.connected = False
            # 不再抛出异常，允许应用在没有数据库的情况下启动

    async def _create_indexes(self):
        """Create database indexes."""
        # Users collection
        await self.database.users.create_index("email", unique=True)
        await self.database.users.create_index("username", unique=True)

        # Products collection
        await self.database.products.create_index("user_id")
        await self.database.products.create_index("created_at")

        # Poster generations collection
        await self.database.poster_generations.create_index("user_id")
        await self.database.poster_generations.create_index("product_id")
        await self.database.poster_generations.create_index("status")

        # Video generations collection
        await self.database.video_generations.create_index("user_id")
        await self.database.video_generations.create_index("status")
        await self.database.video_generations.create_index("created_at")

        # Voice generations collection
        await self.database.voice_generations.create_index("user_id")
        await self.database.voice_generations.create_index("status")

        # Email verification codes collection
        await self.database.verification_codes.create_index("email")
        await self.database.verification_codes.create_index("code")
        await self.database.verification_codes.create_index(
            "expires_at",
            expireAfterSeconds=0,  # TTL index: 自动删除过期文档
        )

        # Password reset tokens collection
        await self.database.password_reset_tokens.create_index("email")
        await self.database.password_reset_tokens.create_index("token", unique=True)
        await self.database.password_reset_tokens.create_index(
            "expires_at", expireAfterSeconds=0
        )

        # Team invitations collection
        await self.database.team_invitations.create_index("team_id")
        await self.database.team_invitations.create_index("token", unique=True)
        await self.database.team_invitations.create_index("email")
        await self.database.team_invitations.create_index(
            "expires_at", expireAfterSeconds=0
        )

        logger.info("Database indexes created")

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    @property
    def db(self):
        """Get database instance."""
        return self.database


# Global MongoDB instance
db = MongoDB()


async def connect_mongodb():
    """Initialize MongoDB connection."""
    await db.connect()


async def close_mongodb():
    """Close MongoDB connection."""
    await db.close()
