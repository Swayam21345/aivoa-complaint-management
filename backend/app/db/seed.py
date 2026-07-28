import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User


async def seed_default_admin(db: AsyncSession) -> None:
    """
    Seed default admin and demo role users with deterministic UUIDs if they do not already exist.
    """
    demo_users = [
        {
            "id": uuid.UUID("11111111-1111-1111-1111-11111111111a"),
            "full_name": "System Administrator",
            "email": "admin@aiccms.local",
            "password": "Admin@123",
            "role": "ADMIN",
        },
        {
            "id": uuid.UUID("22222222-2222-2222-2222-22222222222b"),
            "full_name": "QA Manager",
            "email": "qa@aiccms.local",
            "password": "QAManager@123",
            "role": "QA_MANAGER",
        },
        {
            "id": uuid.UUID("33333333-3333-3333-3333-33333333333c"),
            "full_name": "Lead Investigator",
            "email": "investigator@aiccms.local",
            "password": "Investigator@123",
            "role": "INVESTIGATOR",
        },
        {
            "id": uuid.UUID("44444444-4444-4444-4444-44444444444d"),
            "full_name": "Quality Auditor",
            "email": "viewer@aiccms.local",
            "password": "Viewer@123",
            "role": "VIEWER",
        },
    ]

    for user_data in demo_users:
        stmt = select(User).where(User.email == user_data["email"])
        res = await db.execute(stmt)
        existing_user = res.scalar_one_or_none()

        if not existing_user:
            new_user = User(
                id=user_data["id"],
                full_name=str(user_data["full_name"]),
                email=str(user_data["email"]),
                password_hash=hash_password(str(user_data["password"])),
                role=str(user_data["role"]),
                is_active=True,
            )
            db.add(new_user)

    await db.commit()
