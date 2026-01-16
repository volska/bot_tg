from app.domain.enums import UserMode, ScreenCode
from app.storage.repos.user_state_repo import UserStateRepo

async def handle_start(user_id: int, user_state_repo: UserStateRepo) -> None:
    # В будущем здесь будет: отмена draft + release hold и т.п.
    await user_state_repo.set(user_id, UserMode.NONE, ScreenCode.MENU)