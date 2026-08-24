from uuid import UUID

from src.api.schemas.WebSocket.websocket_action import WebSocketAction
from src.infrastructure.websocket.connection_manager import ConnectionManager


class RealTimePublisher:
    def __init__(self, connection_manager: ConnectionManager):
        self._connection_manager = connection_manager

    async def private_chat_deleted(
        self,
        user1_id: UUID,
        user2_id: UUID,
        deleted_by: UUID,
    ) -> None:

        message = {
            "event": WebSocketAction.PRIVATE_CHAT_DELETED,
            "data": {
                "user_id": str(deleted_by),
                "deleted_by": str(deleted_by),
            },
        }

        await self._connection_manager.broadcast_to_users(
            user_ids=[user1_id, user2_id],
            message=message,
        )

    async def group_member_added(
        self,
        group_id: UUID,
        user_id: UUID,
        added_by: UUID,
        existing_member_ids: list[UUID],
    ) -> None:

        message = {
            "event": WebSocketAction.GROUP_MEMBER_ADDED,
            "data": {
                "group_id": str(group_id),
                "user_id": str(user_id),
                "added_by": str(added_by),
            },
        }

        await self._connection_manager.send_personal(user_id=user_id, message=message)

        member_message = {
            "event": WebSocketAction.GROUP_MEMBER_ADDED,
            "data": {
                "group_id": str(group_id),
                "user_id": str(user_id),
                "added_by": str(added_by),
            },
        }

        await self._connection_manager.broadcast_to_users(
            user_ids=existing_member_ids,
            message=member_message,
        )

    async def group_member_removed(
        self,
        group_id: UUID,
        group_name: str,
        user_id: UUID,
        username: str,
        admin_id: UUID,
        remaining_member_ids: list[UUID],
    ) -> None:

        removed_user_message = {
            "event": WebSocketAction.GROUP_MEMBER_REMOVED,
            "data": {
                "group_id": str(group_id),
                "group_name": group_name,
                "user_id": str(user_id),
                "username": username,
                "removed_by": str(admin_id),
            },
        }

        await self._connection_manager.send_personal(
            user_id=user_id,
            message=removed_user_message,
        )

        member_message = {
            "event": WebSocketAction.GROUP_MEMBER_REMOVED,
            "data": {
                "group_id": str(group_id),
                "group_name": group_name,
                "user_id": str(user_id),
                "username": username,
                "removed_by": str(admin_id),
            },
        }

        await self._connection_manager.broadcast_to_users(
            user_ids=remaining_member_ids,
            message=member_message,
        )

    async def group_member_left(
        self,
        group_id: UUID,
        group_name: str,
        user_id: UUID,
        username: str,
        remaining_member_ids: list[UUID],
    ) -> None:

        message = {
            "event": WebSocketAction.GROUP_MEMBER_LEFT,
            "data": {
                "group_id": str(group_id),
                "group_name": group_name,
                "user_id": str(user_id),
                "username": username,
            },
        }

        await self._connection_manager.broadcast_to_users(
            user_ids=remaining_member_ids,
            message=message,
        )

    async def group_deleted(
        self,
        group_id: UUID,
        member_ids: list[UUID],
        deleted_by: UUID,
    ) -> None:

        message = {
            "event": WebSocketAction.GROUP_DELETED,
            "data": {
                "group_id": str(group_id),
                "deleted_by": str(deleted_by),
            },
        }

        await self._connection_manager.broadcast_to_users(
            user_ids=member_ids,
            message=message,
        )

    async def group_chat_deleted(
        self,
        group_id: UUID,
        member_ids: set[UUID],
        deleted_by: UUID,
    ) -> None:

        message = {
            "event": WebSocketAction.GROUP_CHAT_DELETED,
            "request_id": None,
            "data": {
                "group_id": str(group_id),
                "deleted_by": str(deleted_by),
            },
        }

        await self._connection_manager.broadcast_to_users(
            user_ids=member_ids,
            message=message,
        )
