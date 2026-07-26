
from uuid import uuid4

from src.models.Group import Group
from src.models.Message import Message
from src.models.User import User
from src.models.MessageStatus import MessageStatus
from src.core.CustomeLogger import CustomLogger


    
class UserController:

    def __init__(self)->None:
    
        self.users: list[User] = []
        self.messages: list[Message] = []
        self.groups: list[Group] = []
        self.custome_logger= CustomLogger("UserController")
        
  

    
    def signup(self, username: str, email: str, password: str)->User:

        self.custome_logger.debug("Attempting to sign up user", username=username, email=email, password=password)

        if any(user.username == username for user in self.users):

            self.custome_logger.warning(f"Username already exists", username=username)

            raise ValueError("Username already exists.")

        if any(user.email == email for user in self.users):

            self.custome_logger.warning(f"Email already exists", email=email)

            raise ValueError("Email already exists.")

        user = User(username=username,email=email,password=password)

        self.users.append(user)

        self.custome_logger.info("User created", username=username, email=email)

        return user.id


    def login(self, username: str, password: str)-> User | None:

        self.custome_logger.debug("Attempting to log in user", username=username, password=password)
        
        for user in self.users:
            if user.username == username and user.password == password:

                self.custome_logger.info("User logged in successfully", username=username)

                return user
            
        self.custome_logger.error("Failed to log in user", username=username)

        return None

  

    def send_message(self, sender_id: uuid4 , receiver_id: uuid4, content: str)-> Message:

        self.custome_logger.debug("Attempting to send message", sender_id=sender_id, receiver_id=receiver_id, content=content)

        sender = self.get_user_by_id(sender_id)
        receiver = self.get_user_by_id(receiver_id)

        if sender is None:
            self.custome_logger.warning("Sender not found", sender_id=sender_id)
            raise ValueError("Sender not found.")

        if receiver is None:
            self.custome_logger.warning("Receiver not found", receiver_id=receiver_id)
            raise ValueError("Receiver not found.")

        message = Message(sender_id=sender.id,receiver_id=receiver.id,content=content,status=MessageStatus.SENT)
            
        self.messages.append(message)

        self.custome_logger.info("Message sent", sender_id=sender_id, receiver_id=receiver_id, content=content)

        return message



    def get_chat(self, user1_id: uuid4, user2_id: uuid4)-> list[str]:

        self.custome_logger.debug("Attempting to get chat between users", user1_id=user1_id, user2_id=user2_id)

        chat = []

        for msg in self.messages:

            is_user1_to_user2= (msg.sender.id==user1_id and msg.receiver.id==user2_id)

            is_user2_to_user1= (msg.sender.id==user2_id and msg.receiver.id==user1_id)

            if not (is_user1_to_user2 or is_user2_to_user1):
                continue

            if (is_user1_to_user2 or is_user2_to_user1):
                        
                sender = self.get_user_by_id(str(msg.sender_id))


            if (is_user1_to_user2 and msg.receiver_id==user2_id) or (is_user2_to_user1 and msg.receiver_id==user1_id):

                msg.status = MessageStatus.READ

                self.custome_logger.debug("Message marked as read", message_id=msg.id, sender_id=msg.sender_id, receiver_id=msg.receiver_id)


                chat.append({"username": sender.username, "message": msg.content})
                

        self.custome_logger.info("Chat retrieved successfully", user1_id=user1_id, user2_id=user2_id)

        return chat


#شاید اصلا نیازی به این تابع نباشه و میشه از get_chat استفاده کرد
    def get_messages_for_user(self, user_id: uuid4):

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


    def create_group(self, name: str, creator_id: uuid4):

        self.custome_logger.debug("Attempting to create group", name=name, creator_id=creator_id)

        group = Group(name=name, creator_id=creator_id)

        self.custome_logger.info("Group created successfully", group_id=group.id, name=name, creator_id=creator_id)

        self.groups.append(group)
        return group.id
    

    def add_user_to_group(self, group_id: uuid4, creator_id: uuid4, user_id: uuid4):

        self.custome_logger.debug("Attempting to add user to group", group_id=group_id, creator_id=creator_id, user_id=user_id)

        group = next((g for g in self.groups if g.id == group_id), None)
        user = self.get_user_by_id(user_id)

        if creator_id != group.creator_id:
            self.custome_logger.warning("User is not the creator of the group", creator_id=creator_id, group_id=group_id)
            raise ValueError(f"User {creator_id} is not the creator of the group.only the creator can add members to the group.")


        if group is None:

            self.custome_logger.warning("Group not found", group_id=group_id)

            raise ValueError(f"Group {group_id} not found.")

        if user is None:

            self.custome_logger.warning("User not found", user_id=user_id)

            raise ValueError(f"User {user_id} not found.")

        if user in group.members:

            self.custome_logger.warning("User is already in the group", user_id=user_id, group_id=group_id)

            raise ValueError(f"User {user.username} is already in the group.")

        group.members.append(user)

        self.custome_logger.info("User added to group successfully", user_id=user_id, group_id=group_id)
        return f"User {user.username} added to group {group.name}."


    def send_message_to_group(self, group_id: uuid4, sender_id: uuid4, content: str):

        self.custome_logger.debug("Attempting to send message to group", group_id=group_id, sender_id=sender_id, content=content)

        group = next((g for g in self.groups if g.id == group_id), None)
        sender = self.get_user_by_id(sender_id)

        if group is None:
            self.custome_logger.warning("Group not found", group_id=group_id)
            raise ValueError(f"Group {group_id} not found.")

        if sender is None:
            self.custome_logger.warning("Sender not found", sender_id=sender_id)
            raise ValueError(f"User {sender_id} not found.")

        if sender not in group.members:
            self.custome_logger.warning("Sender is not a member of the group", sender_id=sender_id, group_id=group_id)
            raise ValueError(f"User {sender_id} is not a member of the group.")

        message = Message(sender_id=sender.id, content=content, status=MessageStatus.SENT)
        group.messages.append(message)
        message.group_id = group.id

        self.custome_logger.info("Message sent to group successfully", group_id=group_id, sender_id=sender_id, content=content)

        return message

    def get_group_chat(self, group_id: uuid4):

        self.custome_logger.debug("Attempting to get group chat", group_id=group_id)

        group = next((g for g in self.groups if g.id == group_id), None)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise ValueError(f"Group {group_id} not found.")

        chat = []
        for msg in group.messages:
            sender = self.get_user_by_id(str(msg.sender_id))
            chat.append({"username": sender.username, "message": msg.content})

        self.custome_logger.info("Group chat retrieved successfully", group_id=group_id)

        return chat


    def _get_user_by_id(self, user_id: uuid4):
        self.custome_logger.debug("Attempting to get user by ID", user_id=user_id)

        for user in self.users:
            if user.id == user_id:
                return user

        return None

    def _get_all_users(self):
        self.custome_logger.debug("Attempting to get all users")
        user_list = []
        for user in self.users:
            user_list.append(f"User ID: {user.id}, Username: {user.username}")
        return user_list


    def get_all_groups(self):
        self.custome_logger.debug("Attempting to get all groups")
        group_list = []
        for group in self.groups:
            group_list.append(f"Group ID: {group.id}, Group Name: {group.name}")
        return group_list


    







 

        
