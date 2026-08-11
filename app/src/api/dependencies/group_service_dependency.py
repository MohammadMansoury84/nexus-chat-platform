
from fastapi import Depends
from app.src.domain.repositories_Interface.group_message_repository import GroupMessageRepository
from app.src.domain.repositories_Interface.group_repository import GroupRepository
from app.src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure.repositories_implementation.group_message_repository_impl import GroupMessageRepositoryImpl
from src.infrastructure.repositories_implementation.group_repository_impl import GroupRepositoryImpl
from src.infrastructure.repositories_implementation.user_repository_impl import UserRepositoryImpl
from src.application.service.services_implementation.group_service_impl import GroupServiceImpl







user_repository=UserRepositoryImpl()
group_repository=GroupRepositoryImpl()
group_message_repository=GroupMessageRepositoryImpl()

def get_user_repository():
    return user_repository

def get_group_repository():
    return group_repository

def get_group_message_repository():
    return group_message_repository

def get_group_service(
        group_repository: GroupRepository=Depends(get_group_repository),
        group_message_repository : GroupMessageRepository=Depends(get_group_message_repository),
        user_repository: UserRepository=Depends(get_user_repository),   
        ):
    return GroupServiceImpl(
        user_repository=user_repository,
        group_repository=group_repository,
        group_message_repository=group_message_repository
        )    



