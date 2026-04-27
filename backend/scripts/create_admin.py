# scripts/create_admin.py
import asyncio
import sys
sys.path.insert(0, ".")

import app.shared.database.registry  # noqa — charge tous les modèles

from app.shared.database.session import SessionLocal
from app.modules.users.models import User
from app.shared.security.password import hash_password

async def create_admin(email: str, password: str, full_name: str):
    async with SessionLocal() as db:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_active=True,
            is_admin=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ Admin créé : {user.email} (id={user.id})")

if __name__ == "__main__":
    asyncio.run(create_admin(
        email="admin@deutschtest.com",
        password="Admin1234",
        full_name="Admin DeutschTest",
    ))