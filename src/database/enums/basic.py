from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"

class TimeRange(Enum):
    DAY = 1
    WEEK = 7
    MONTH = 30
    QUARTER = 90

class NotificationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class UserActivityType(Enum):
    LOGIN = "login"
    COMMAND = "command"
    NOTIFICATION = "notification"
    SETTINGS_UPDATE = "settings_update"