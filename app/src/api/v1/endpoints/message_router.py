from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends,status

message_router = APIRouter(
    prefix="/message",
    tags=["Message"],
)