
from uuid import UUID
from src.repository.UserRepository import UserRepository
from src.repository.GroupRepository import GroupRepository
from src.entities.Group import Group
from src.entities.Message import Message
from src.entities.User import User
from src.entities.MessageStatus import MessageStatus
from src.core.CustomeLogger import CustomLogger
from src.entities.GroupMessage import GroupMessage
from src.Exceptions import (

    UserNotFoundError,
    AuthorizationError,
    GroupNotFoundError,
    UserAlreadyInGroupError
)



class GroupService:

    def __init__(self,user_repository: UserRepository,group_repository: GroupRepository) -> None:
        self._user_repository = user_repository
        self._group_repository = group_repository
        
        self.custome_logger= CustomLogger(self.__class__.__name__)


    def create_group(self, name: str, creator_id: UUID)-> UUID:
        
        self.custome_logger.debug("Attempting to create group", name=name, creator_id=creator_id)

        group = Group(name=name, creator_id=creator_id)
        target_user=self._user_repository.get_by_id(user_id=creator_id)

        if target_user is None:
            self.custome_logger.warning("User not found", user_id=creator_id)
            raise UserNotFoundError(f"User {creator_id} not found.")

        target_user.groups_created.append(group)
        target_user.joined_groups.append(group)
        group.members.append(target_user)
        self._group_repository.add(group)

        self.custome_logger.info("Group created successfully", group_id=group.id, name=name, creator_id=creator_id)

        return group.id

    def add_user_to_group(self, group_id: UUID, creator_id: UUID, user_id: UUID)->str:

        
        self.custome_logger.debug("Attempting to add user to group", group_id=group_id, creator_id=creator_id, user_id=user_id)

        group = self._group_repository.get_by_id(group_id=group_id)
        user = self._user_repository.get_by_id(user_id)

        if user is None:

            self.custome_logger.warning("User not found", user_id=user_id)

            raise UserNotFoundError(f"User {user_id} not found.")

        if group is None:

            self.custome_logger.warning("Group not found", group_id=group_id)

            raise GroupNotFoundError(f"Group {group_id} not found.")
        

        if creator_id != group.creator_id:
            self.custome_logger.warning("User is not the creator of the group", creator_id=creator_id, group_id=group_id)
            raise AuthorizationError(f"User {creator_id} is not the creator of the group.only the creator can add members to the group.")



        if user in group.members:

            self.custome_logger.warning("User is already in the group", user_id=user_id, group_id=group_id)

            raise UserAlreadyInGroupError(f"User {user.username} is already in the group.") 

        group.members.append(user)
        user.joined_groups.append(group)

        self.custome_logger.info("User added to group successfully", user_id=user_id, group_id=group_id)
        return f"User {user.username} added to group {group.name}."


    def send_message_to_group(self, group_id: UUID, sender_id: UUID, content: str)->Message:
        
        self.custome_logger.debug("Attempting to send message to group", group_id=group_id, sender_id=sender_id, content=content)

        group = self._group_repository.get_by_id(group_id=group_id)
        sender = self._user_repository.get_by_id(sender_id)

        if group is None:
            self.custome_logger.warning("Group not found", group_id=group_id)
            raise GroupNotFoundError(f"Group {group_id} not found.")

        if sender is None:
            self.custome_logger.warning("Sender not found", sender_id=sender_id)
            raise UserNotFoundError(f"User {sender_id} not found.")

        if sender not in group.members:
            self.custome_logger.warning("Sender is not a member of the group", sender_id=sender_id, group_id=group_id)
            raise UserNotFoundError(f"User {sender_id} is not a member of the group.")

        message = GroupMessage(sender_id=sender.id,group_id = group.id ,content=content, status=MessageStatus.SENT)
        group.messages.append(message)
        

        self.custome_logger.info("Message sent to group successfully", group_id=group_id, sender_id=sender_id, content=content)

        return message

    def get_group_chat(self, group_id: UUID)-> list[dict] | None:
        
        self.custome_logger.debug("Attempting to get group chat", group_id=group_id)

        group = self._group_repository.get_by_id(group_id=group_id)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise GroupNotFoundError(f"Group {group_id} not found.")

        chat = []
        if group.messages:
            for msg in group.messages:
                sender = self._user_repository.get_by_id(msg.sender_id)
                
                chat.append({"username": sender.username, "message": msg.content})

            self.custome_logger.info("Group chat retrieved successfully", group_id=group_id)
            return chat
        else:
            return None



    def get_group_by_id(self, group_id : UUID)-> Group | None:
        return self._group_repository.get_by_id(group_id=group_id)
            
            

    def get_all_groups_for_show_users(self)->list[dict]:
        group_list = []
        for group in self._group_repository.list_all():
            group_list.append(f"Group ID: {group.id}, Group Name: {group.name}")
        return group_list
    

    def get_all_Groups(self)->list[Group]:
        return self._group_repository.list_all()



        


    




    

        
        
        
   
