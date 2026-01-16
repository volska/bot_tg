from app.domain.enums import UserMode, ScreenCode
from app.domain.models import UserState
from app.storage.db import DB

class UserStateRepo:
    def __init__(self, db: DB):
        self._db = db

    async def get_or_create(self, user_id: int) -> UserState:
        with self._db.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id, mode, screen FROM user_state WHERE user_id=%s",
                    (user_id,),
                )
                row = cur.fetchone()
                if row:
                    return UserState(
                        user_id=int(row["user_id"]),
                        mode=UserMode(row["mode"]),
                        screen=ScreenCode(row["screen"]),
                    )

                cur.execute(
                    "INSERT INTO user_state(user_id, mode, screen) VALUES (%s, 'NONE', 'MENU')",
                    (user_id,),
                )
                conn.commit()
                return UserState(user_id=user_id, mode=UserMode.NONE, screen=ScreenCode.MENU)

    async def set(self, user_id: int, mode: UserMode, screen: ScreenCode) -> None:
        with self._db.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_state(user_id, mode, screen, updated_at)
                    VALUES (%s, %s, %s, now())
                    ON CONFLICT (user_id) DO UPDATE
                      SET mode=EXCLUDED.mode, screen=EXCLUDED.screen, updated_at=now()
                    """,
                    (user_id, mode.value, screen.value),
                )
                conn.commit()
