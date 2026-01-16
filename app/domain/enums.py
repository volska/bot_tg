from enum import Enum

class UserMode(str, Enum):
    NONE = "NONE"
    BOOKING = "BOOKING"
    QUESTION = "QUESTION"
    GROUP_PASSWORD = "GROUP_PASSWORD"

class ScreenCode(str, Enum):
    MENU = "MENU"
    B001 = "B001"
    B002 = "B002"
    B003 = "B003"
    B003B = "B003B"
    B004 = "B004"
    B005 = "B005"
    B006 = "B006"
    Q1 = "Q1"
    Q2 = "Q2"
    G1 = "G1"
    G2 = "G2"
    W1 = "W1"