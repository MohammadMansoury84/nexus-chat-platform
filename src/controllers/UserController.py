


import src.models.Group
import src.models.Message
from pydantic import BaseModel, Field
import src.models.User

#یادت نره try except بزارم
class UserController():

    
    def __init__(self):
        users =list[src.models.User.User]
        messages= list[src.models.Message.Message]
        groups= list[src.models.Group.Group]
    
  

    
    def signup(self, username: str, email: str, password: str):
        if (user.username == username for user in self.users):
             ValueError("Username already exists.")

        if any(user.email == email for user in self.users):
            raise ValueError("Email already exists.")

        user = src.models.User.User(username=username,email=email,password=password)

        self.users.append(user)
        return user


    def login(self, username: str, password: str):
        for user in self.users:
            if user.username == username and user.password == password:
                return user
        return None

  

    def send_message(self, sender_id: str, receiver_id: str, content: str):

        sender = self.get_user_by_id(sender_id)
        receiver = self.get_user_by_id(receiver_id)

        if sender is None:
            raise ValueError("Sender not found.")

        if receiver is None:
            raise ValueError("Receiver not found.")

        message = src.models.Message.Message(sender_id=sender.id,receiver_id=receiver.id,content=content,status="sent")
            
        self.messages.append(message)

        return message



    def get_chat(self, user1_id: str, user2_id: str):

        chat = []

        for msg in self.messages:

            if (msg.sender_id == user1_id and msg.receiver_id == user2_id) or (msg.sender_id == user2_id and msg.receiver_id == user1_id):
                        
                sender = self.get_user_by_id(str(msg.sender_id))

                if msg.receiver_id == user1_id:
                    msg.status = "read"

                chat.append({"username": sender.username, "message": msg.content})
                    
        return chat


    def get_messages_for_user(self, user_id: str):

        chat = []

        user = self.get_user_by_id(user_id)

        if user is None:
            return []

        for msg in self.messages:

            if (msg.sender_id == user.id or msg.receiver_id == user.id):

                if msg.receiver_id == user.id:
                    msg.status = "read"

                sender = self.get_user_by_id(str(msg.sender_id))

                chat.append({"username": sender.username,"message": msg.content})
        return chat


    def create_group(self, name: str, creator_id: str):
        group = src.models.Group.Group(name=name, creator_id=creator_id)
        self.groups.append(group)
        return group.id

    def add_user_to_group(self, group_id: str, user_id: str):
        group = next((g for g in self.groups if str(g.id) == group_id), None)
        user = self.get_user_by_id(user_id)

        if group is None:
            raise ValueError("Group not found.")

        if user is None:
            raise ValueError("User not found.")

        if user in group.members:
            raise ValueError("User already in the group.")

        group.members.append(user)
        return f"User {user.username} added to group {group.name}."

    

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

    def ge_all_groups(self):
        group_list = []
        for group in self.groups:
            group_list.append(f"Group ID: {group.id}, Group Name: {group.name}")
        return group_list


    







 

        
