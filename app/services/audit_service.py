class AuditService:
    def __init__(self, db: DB):
        self._db = db

    async def log(
        self,
        *,
        user_id: int | None,
        event_type: str,
        payload: dict | None,
        mode_before: UserMode | None,
        screen_before: ScreenCode | None,
        mode_after: UserMode | None,
        screen_after: ScreenCode | None,
        result: str,
        error_code: str | None = None,
    ) -> None:
        with self._db.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_events(
                        user_id, event_type, payload,
                        mode_before, screen_before, mode_after, screen_after,
                        result, error_code
                    )
                    VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        event_type,
                        json.dumps(payload or {}),
                        (mode_before.value if mode_before else None),
                        (screen_before.value if screen_before else None),
                        (mode_after.value if mode_after else None),
                        (screen_after.value if screen_after else None),
                        result,
                        error_code,
                    ),
                )
                conn.commit()
