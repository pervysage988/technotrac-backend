# app/seed.py
import asyncio
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.db.models.equipment import Equipment, EquipmentStatus
from app.db.models.user import User


async def seed():
    async with AsyncSessionLocal() as session:
        # get the first user (owner)
        result = await session.execute(select(User))
        owner = result.scalars().first()

        if not owner:
            print("⚠️ No users found. Please create a user first.")
            return

        eq1 = Equipment(
            name="Tractor John Deere 5105",
            description="45 HP, power steering, 4WD",
            location="Village A",
            status=EquipmentStatus.APPROVED,
            owner_id=owner.id,
        )

        eq2 = Equipment(
            name="Rotavator",
            description="6 ft, multi-speed gear box",
            location="Village B",
            status=EquipmentStatus.APPROVED,
            owner_id=owner.id,
        )

        session.add_all([eq1, eq2])
        await session.commit()
        print("✅ Seeded 2 equipment items.")


if __name__ == "__main__":
    asyncio.run(seed())
