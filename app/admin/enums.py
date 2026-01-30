class Roles(str, Enum):
    ADMIN = "admin"  # Administrator (어드민)
    MOD = "mod"  # Moderator (운영자)
    RM = "rm"  # Ranked Manager (맵 랭크하는사람)
    LV = "lv"  # Level Validator (맵 레벨 정하는사람 예: 랭커들, 겜잘알들, 운영자jot목팸들)
    USER = "user"  # Regular User (일반 유저)

