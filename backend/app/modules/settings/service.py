# app/modules/settings/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.settings.models import AppSetting

class AppSettingsService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, key: str, default: str = "") -> str:
        result = await self.db.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    async def set(self, key: str, value: str, description: str | None = None) -> AppSetting:
        result = await self.db.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            await self.db.commit()
            return setting
        setting = AppSetting(key=key, value=value, description=description)
        self.db.add(setting)
        await self.db.commit()
        return setting

    async def is_free_access_mode(self) -> bool:
        val = await self.get("free_access_mode", "false")
        return val.lower() == "true"