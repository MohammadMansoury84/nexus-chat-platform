from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from src.api.dependencies.auth_service_dependency import get_current_user_id
from src.api.dependencies.group_service_dependency import get_group_service
from src.api.schemas.Request.group.add_user_to_group_request import AddUserToGroupRequest
from src.api.schemas.Request.group.create_group_request import CreateGroupRequest
from src.api.schemas.Request.group.send_group_message_request import SendGroupMessageRequest
from src.api.schemas.Response.group.create_group_response import CreateGroupResponse
from src.api.schemas.Response.group.get_group_by_id_response import GetGroupByIdResponse
from src.api.schemas.Response.group.group_chat_message_response import (
    GroupChatMessageResponse,
)
from src.api.schemas.Response.group.group_member_response import GroupMemberResponse
from src.api.schemas.Response.group.group_membership_action_response import (
    GroupMembershipActionResponse,
)
from src.api.schemas.Response.group.group_message_response import GroupMessageResponse
from src.api.schemas.Response.group.group_summary_response import GroupSummaryResponse
from src.api.schemas.Response.response import Response
from src.application.service.service_Interface.group_service import GroupService

group_router = APIRouter(
    prefix="/groups",
    tags=["Group"],
    dependencies=[Depends(get_current_user_id)],
)


@group_router.post(
    "/create_group",
    response_model=Response[CreateGroupResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
    request: CreateGroupRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
) -> Response[CreateGroupResponse]:

    group = await group_service.create_group(
        name=request.name,
        creator_id=current_user_id,
    )

    return Response[CreateGroupResponse](
        data=CreateGroupResponse(
            group_id=group.group_id,
            group_name=group.group_name,
            creator_id=group.creator_id,
        ),
        message="Group created successfully",
    )


@group_router.post(
    "/{group_id}/members",
    response_model=Response[bool],
    status_code=status.HTTP_200_OK,
)
async def add_user_to_group(
    group_id: UUID,
    request: AddUserToGroupRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
) -> Response[bool]:

    result = await group_service.add_user_to_group(
        group_id=group_id,
        creator_id=current_user_id,
        user_id=request.user_id,
    )

    return Response[bool](
        data=result,
        message="User added to group successfully",
    )


@group_router.post(
    "/{group_id}/messages",
    response_model=Response[GroupMessageResponse],
    status_code=status.HTTP_200_OK,
)
async def send_message_to_group(
    group_id: UUID,
    request: SendGroupMessageRequest,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[GroupMessageResponse]:

    message = await group_service.send_message_to_group(
        group_id=group_id,
        sender_id=current_user_id,
        content=request.content,
    )

    return Response[GroupMessageResponse](
        data=GroupMessageResponse(
            sender_id=message.sender_id,
            group_id=message.group_id,
            content=message.content,
            status=message.status,
        ),
        message="Message sent to group successfully",
    )


@group_router.get(
    "/{group_id}/messages",
    response_model=Response[list[GroupChatMessageResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_group_chat(
    group_id: UUID,
    group_service: Annotated[GroupService, Depends(get_group_service)],
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
) -> Response[list[GroupChatMessageResponse]]:

    chat = await group_service.get_group_chat(group_id=group_id, sender_id=current_user_id)

    data = [
        GroupChatMessageResponse(
            sender_id=message.sender_id,
            username=message.username,
            content=message.content,
        )
        for message in chat
    ]

    return Response[list[GroupChatMessageResponse]](
        data=data,
        message=(
            "Group chat retrieved successfully."
            if chat
            else "There is no chat history in this group."
        ),
    )


@group_router.get(
    "/by-id/{group_id}",
    response_model=Response[GetGroupByIdResponse],
    status_code=status.HTTP_200_OK,
)
async def get_group_by_id(
    group_id: UUID,
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[GetGroupByIdResponse]:

    group = await group_service.get_group_by_id(group_id=group_id)

    return Response[GetGroupByIdResponse](
        data=GetGroupByIdResponse(
            group_id=group.group_id,
            group_name=group.group_name,
            creator_id=group.creator_id,
        ),
        message="Group retrieved successfully.",
    )


@group_router.get(
    "/my-groups",
    response_model=Response[list[GroupSummaryResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_all_groups_for_show_users(
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[list[GroupSummaryResponse]]:

    groups = await group_service.get_all_groups_for_show_users(user_id=current_user_id)

    data = [
        GroupSummaryResponse(
            group_id=group.group_id,
            group_name=group.group_name,
        )
        for group in groups
    ]

    return Response[list[GroupSummaryResponse]](
        data=data,
        message=(
            "Groups retrieved successfully."
            if groups
            else "You have not joined or created any groups yet."
        ),
    )


@group_router.get(
    "/all",
    response_model=Response[list[GroupSummaryResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user_id)],
)
async def get_all_groups(
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[list[GroupSummaryResponse]]:

    groups = await group_service.get_all_groups()

    data = [
        GroupSummaryResponse(
            group_id=group.group_id,
            group_name=group.group_name,
        )
        for group in groups
    ]

    return Response[list[GroupSummaryResponse]](
        data=data,
        message=("Groups retrieved successfully." if groups else "No groups found."),
    )


@group_router.delete(
    "/{group_id}",
    response_model=Response[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_group_by_id(
    group_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[bool]:

    result = await group_service.delete_group_by_id(
        user_id=current_user_id,
        group_id=group_id,
    )

    return Response[bool](
        data=result,
        message="Group deleted successfully.",
    )


@group_router.get(
    "/{group_id}/members",
    response_model=Response[list[GroupMemberResponse]],
    status_code=status.HTTP_200_OK,
)
async def show_group_members(
    group_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[list[GroupMemberResponse]]:

    members = await group_service.show_group_member(
        user_id=current_user_id,
        group_id=group_id,
    )

    return Response[list[GroupMemberResponse]](
        data=[
            GroupMemberResponse(
                id=member.id,
                username=member.username,
            )
            for member in members
        ],
        message=(
            "Group members retrieved successfully."
            if members
            else "This group has no members."
        ),
    )


@group_router.delete(
    "/{group_id}/messages",
    response_model=Response[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_group_chat_history(
    group_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[bool]:

    result = await group_service.delete_group_chat_history(
        user_id=current_user_id,
        group_id=group_id,
    )

    return Response[bool](
        data=result,
        message="Group chat history deleted successfully.",
    )


@group_router.delete(
    "/{group_id}/members/{user_id}",
    response_model=Response[GroupMembershipActionResponse],
    status_code=status.HTTP_200_OK,
)
def remove_user_from_group(
    group_id: UUID,
    user_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    group_service: Annotated[
        GroupService,
        Depends(get_group_service),
    ],
) -> Response[GroupMembershipActionResponse]:

    result = group_service.remove_user_from_group(
        admin_id=current_user_id,
        group_id=group_id,
        user_id=user_id,
    )

    return Response[GroupMembershipActionResponse](
        data=GroupMembershipActionResponse(
            action=result.action,
            group_id=result.group_id,
            group_name=result.group_name,
            user_id=result.user_id,
            username=result.username,
        ),
        message="Group membership updated successfully.",
    )
