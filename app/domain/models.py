from dataclasses import dataclass
from app.domain.enums import UserMode, ScreenCode

@dataclass
class UserState:
    user_id: int
    mode: UserMode
    screen: ScreenCode