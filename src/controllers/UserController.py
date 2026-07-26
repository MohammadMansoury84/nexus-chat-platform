
from pydantic import BaseModel, Field
from src.models.Group import Group
from src.models.Message import Message
from src.models.User import User
from src.models.MessageStatus import MessageStatus


    
class UserController:

    def __init__(self)->None:
        self.users: list[User] = []
        self.messages: list[Message] = []
        self.groups: list[Group] = []
        
  

    
    def signup(self, username: str, email: str, password: str)->User:
        if any(user.username == username for user in self.users):
            raise ValueError("Username already exists.")

        if any(user.email == email for user in self.users):
            raise ValueError("Email already exists.")

        user = User(username=username,email=email,password=password)

        self.users.append(user)
        return user


    def login(self, username: str, password: str)-> User | None:
        for user in self.users:
            if user.username == username and user.password == password:
                return user
        return None

  

    def send_message(self, sender_id: str, receiver_id: str, content: str)-> Message:

        sender = self.get_user_by_id(sender_id)
        receiver = self.get_user_by_id(receiver_id)

        if sender is None:
            raise ValueError("Sender not found.")

        if receiver is None:
            raise ValueError("Receiver not found.")

        message = Message(sender_id=sender.id,receiver_id=receiver.id,content=content,status=MessageStatus.SENT)
            
        self.messages.append(message)

        return message



    def get_chat(self, user1_id: str, user2_id: str)-> list[str]:

        chat = []

        for msg in self.messages:

            is_user1_to_user2= (msg.sender.id==user1_id and msg.raiseiver.id==user2_id)

            is_user2_to_user1= (msg.sender.id==user2_id and msg.receiver.id==user1_id)

            if not (is_user1_to_user2 or is_user2_to_user1):
                continue

            if (is_user1_to_user2 or is_user2_to_user1):
                        
                sender = self.get_user_by_id(str(msg.sender_id))


            if (is_user1_to_user2 and msg.receiver_id==user2_id) or (is_user2_to_user1 and msg.receiver_id==user1_id):
                msg.status = MessageStatus.READ


                chat.append({"username": sender.username, "message": msg.content})
                    
        return chat


#شاید اصلا نیازی به این تابع نباشه و میشه از get_chat استفاده کرد
    def get_messages_for_user(self, user_id: str):

        chat = []

        user = self.get_user_by_id(user_id)

        if user is None:
             raise ValueError(f"User {user_id} not found.")


        for msg in self.messages:

            if (msg.sender_id == user.id or msg.receiver_id == user.id):

                if msg.receiver_id == user.id:
                    msg.status = MessageStatus.READ

                sender = self.get_user_by_id(str(msg.sender_id))

                chat.append({"username": sender.username,"message": msg.content})
        return chat


    def create_group(self, name: str, creator_id: str):
        group = Group(name=name, creator_id=creator_id)
        self.groups.append(group)
        return group.id
    

    def add_user_to_group(self, group_id: str, creator_id: str,user_id: str):
        group = next((g for g in self.groups if str(g.id) == group_id), None)
        user = self.get_user_by_id(user_id)

        if creator_id != str(group.creator_id):
            raise ValueError(f"User {creator_id} is not the creator of the group.only the creator can add members to the group.")


        if group is None:
            raise ValueError(f"Group {group_id} not found.")

        if user is None:
            raise ValueError(f"User {user_id} not found.")

        if user in group.members:
            
            raise ValueError(f"User {user.username} is already in the group.")

        group.members.append(user)
        return f"User {user.username} added to group {group.name}."


    def send_message_to_group(self, group_id: str, sender_id: str, content: str):
        group = next((g for g in self.groups if str(g.id) == group_id), None)
        sender = self.get_user_by_id(sender_id)

        if group is None:
            raise ValueError(f"Group {group_id} not found.")

        if sender is None:
            raise ValueError(f"User {sender_id} not found.")

        if sender not in group.members:
            raise ValueError(f"User {sender_id} is not a member of the group.")

        message = Message(sender_id=sender.id, content=content, status=MessageStatus.SENT)
        group.messages.append(message)
        message.group_id = group.id

        return message

    def get_group_chat(self, group_id: str):
        group = next((g for g in self.groups if str(g.id) == group_id), None)

        if group is None:
            raise ValueError(f"Group {group_id} not found.")

        chat = []
        for msg in group.messages:
            sender = self.get_user_by_id(str(msg.sender_id))
            chat.append({"username": sender.username, "message": msg.content})

        return chat


    def get_user_by_id(self, user_id: str):

        for user in self.users:
            if str(user.id) == str(user_id):
                return user

        return None

    def get_all_users(self):
        user_list = []
        for user in self.users:
            user_list.append(f"User ID: {user.id}, Username: {user.username}")
        return user_list


    def get_all_groups(self):
        group_list = []
        for group in self.groups:
            group_list.append(f"Group ID: {group.id}, Group Name: {group.name}")
        return group_list


    







 

        
