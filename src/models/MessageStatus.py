from enum import Enum

class MessageStatus(str,Enum):
    SENT = "sent"
    DELIVERED="delivered"
    READ = "read"

