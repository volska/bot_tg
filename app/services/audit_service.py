from app.domain.enums import UserMode, ScreenCode
from app.domain.models import UserState
from app.storage.db import DB

class UserStateRepo:
    def __init__(self, db: DB):
        self._db = db

    async def get_or_create(self, user_id: int) -> UserState:
        async with self._db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, mode, screen FROM user_state WHERE user_id=$1",
                user_id,
            )
            if row:
                return UserState(
                    user_id=int(row["user_id"]),
                    mode=UserMode(row["mode"]),
                    screen=ScreenCode(row["screen"]),
                )

            await conn.execute(
                "INSERT INTO user_state(user_id, mode, screen) VALUES ($1, 'NONE', 'MENU')",
                user_id,
            )
            return UserState(user_id=user_id, mode=UserMode.NONE, screen=ScreenCode.MENU)

    async def set(self, user_id: int, mode: UserMode, screen: ScreenCode) -> None:
        async with self._db.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_state(user_id, mode, screen, updated_at)
                VALUES ($1, $2, $3, now())
                ON CONFLICT (user_id) DO UPDATE SET mode=EXCLUDED.mode, screen=EXCLUDED.screen, updated_at=now()
                """,
                user_id,
                mode.value,
                screen.value,
            )