from src.controllers.UserController import UserController
from src.models.User import User
from src.models.Group import Group
from typing import Optional


class UserView():

        def __init__(self, controller: UserController)->None:
            self.controller = controller
            self.login_users :list[User]=[]
            self.current_user : User


        def show_Main_menu(self):

            while True:

                print("\n====== Messenger ======")


            
                print("--------------------------------")
                print("1. Signup")
                print("2. Login")
                print("3. Send Private Message")
                print("4. Show Private Chat")
                print("5. Change Current User")
                print("6. Show Logged-in Users")
                print("7. Show Groups")
                print("8. Create Group")
                print("9. Add User to Group")
                print("10. Send Message to Group")
                print("11. Show Group Chat")
                print("12. Logout Current User")
                print("13. Exit")

                choice = input("Enter your choice: ")

                try:
                    if choice == "1":
                        self.signup()

                    elif choice == "2":
                        self.login()

                    elif choice == "3":
                        self.send_message()

                    elif choice == "4":
                        self.show_private_chat()

                    elif choice == "5":
                        self.change_user()

                    elif choice == "6":
                        self.show_logged_in_users()

                    elif choice == "7":
                        self.show_groups()

                    elif choice == "8":
                        self.create_group()

                    elif choice == "9":
                        self.add_user_to_group()

                    elif choice == "10":
                        self.send_message_to_group()

                    elif choice == "11":
                        self.show_group_chat()

                    elif choice == "12":
                        self.logout()

                    elif choice == "13":
                        print("exiting...")
                        break


                    else:
                        print("Invalid choice.")

                except Exception as e:
                    print(f"Error: {e}")


        def signup(self):

            print("\n========== Signup ==========")

            userName=input("username: ").strip()
            email=input("email : ").strip()
            password=input("password : ").strip()

            user_id=self.controller.signup(username=userName,email=email,password=password)

            if user_id is not None:
                    print(f"User created successfully.login first")
                    print(f"User ID: {user_id}")
            else:
                print("sign up feild")
                return



        def login(self)->None:
            print("\n========== Login ==========")

            userName=input("username: ").strip()
            password=input("password : ").strip()

            user=self.controller.login(username=userName,password=password)

            if user is None:
                    print("Username or password is incorrect.")
                    return

            if user not in self.login_users:
                self.login_users.append(user)

            self.current_user = user

            print(f"{user.username} logged in successfully.")


        def logout(self) -> None:

            if not self._require_login():
                return

            user = self.current_user

            if user in self.login_users:
                self.login_users.remove(user)

            if self.login_users:
                self.current_user = self.login_users[-1]
                print(f"{user.username} logged out.")
                print(f"Current user changed to {self.current_user.username}.")
            else:
                self.current_user = None
                print(f"{user.username} logged out.")
                print("No user is currently logged in.")


        def change_user(self) -> None:
            if not self._require_login():
                return

            if not self.login_users:
                print("No logged-in users.")
                return

            print("\n========== Change User ==========")

            users = self._get_other_logged_in_users()

            if users :

                user = self._select_user(users=users,title="Choose current user")
                
                if user is None:
                    print("user not found")
                    return

                self.current_user = user
                print(f"Current user changed to {user.username}.")
            else:
                print("No other logged-in users are available.")



        def show_logged_in_users(self) -> None:
            if not self._require_login():
                return

            if not self.login_users:
                print("No logged-in users.")
                return

            print("\n========== Logged-in Users ==========")

            for index, user in enumerate(self.login_users, start=1):

                current_sign = ""

                if self.current_user is not None:
                    if user.id == self.current_user.id:
                        current_sign = " <- Current User"

                print(f"{index}. {user.username}{current_sign}")



        def send_message(self) -> None:

            if not self._require_login():
                return


            users = self._get_other_logged_in_users()

            if not users:
                print("No other logged-in users are available.")
                return

            print("\n========== Send Private Message ==========")

            receiver = self._select_user(users=users,title="Who do you want to message?")
                
                
            if receiver is None:
                print("receiver not founf")
                return

            print(f"\n--- Chat with {receiver.username} ---")
            print("Write 'exit' to leave the chat.")
            print("Write 'change' to change receiver account.")
            print("-----------------------------------")

        
            chat_history = self.controller.get_chat(self.current_user.id, receiver.id)
            if chat_history:
                print("\n[Previous Messages]")
                self._print_chat(chat_history)
                print("-------------------\n")
            else:
                print("You have no history with this user.")

            while True:
                content = input(f"{self.current_user.username}: ").strip()

                if content.lower() == "exit":
                    print("Private chat closed.")
                    break
                
                if content.lower() == "change":
                    new_receiver = self._select_user(users=users,title="Who do you want to message?")
                        
                    if new_receiver is not None:
                        receiver = new_receiver
                        print(f"\n--- Chat with {receiver.username} ---")
                    
           
                        chat_history = self.controller.get_chat(self.current_user.id, receiver.id)
                        if chat_history:
                            print("\n[Previous Messages]")
                            self._print_chat(chat_history)
                            print("-------------------\n")
                            
                        else:
                            print("You have no history with this user.")

                        continue

                if not content:
                    print("Message cannot be empty.")
                    continue

                try:
                    self.controller.send_message(sender_id=self.current_user.id,receiver_id=receiver.id,content=content)
                        
                except Exception as e:
                    print(f"Message could not be sent: {e}")

                

        def show_private_chat(self) -> None:

            if not self._require_login():
                return

            users = self._get_other_logged_in_users()

            if not users:
                print("No other logged-in users are available.")
                return

            print("\n========== Private Chat ==========")

            other_user = self._select_user(users=users,title="Choose a user")
                

            if other_user is None:
                print("user not found")
                return

            chat = self.controller.get_chat(user1_id=self.current_user.id,user2_id=other_user.id)
                

            print(
                f"\n========== "
                f"chat between :{self.current_user.username} and {other_user.username}"
                f" =========="
            )
            if chat:
                self._print_chat(chat)
            else:
                print("You have no history with this user.")



        def show_groups(self) -> None:
            if not self._require_login():
                return
            
            print("\n========== Groups ==========")

            groups = self.current_user.joined_groups

            if not groups:
                print("No groups have been found.")
                return

            for index, group in enumerate(groups, start=1):
                print(f"{index}. {group.name}")

        def create_group(self) -> None:

            if not self._require_login():
                return

            print("\n========== Create Group ==========")

            name = input("Group name: ").strip()


            group_id = self.controller.create_group(name=name,creator_id=self.current_user.id)

            if group_id:
                print("Group created successfully.")
                print(f"Group ID: {group_id}")
            else:
                print("Group created Unsuccessfully.")
            

        def add_user_to_group(self) -> None:

            if not self._require_login():
                return

            if not self.current_user.groups_created:
                print("No groups have been created.")
                return

            print("\n========== Add User to Group ==========")

            group = self._select_group(groups=self.current_user.groups_created,title="Choose a group")
                
            if group is None:
                print("group not found")
                return

            available_users = []

            for user in self.login_users:

                is_not_member = True

                for member in group.members:
                    if member.id == user.id:
                        is_not_member = False
                        break

                if is_not_member:
                    available_users.append(user)
                
            if not available_users:
                print("All registered users are already members of this group.")
                return

            user = self._select_user(users=available_users,title="Choose a user to add")
                
            if user is None:
                print("user not found")
                return

            result = self.controller.add_user_to_group(group_id=group.id,creator_id=self.current_user.id,user_id=user.id)
    
            print(result)

        def send_message_to_group(self) -> None:

            if not self._require_login():
                return
            
            

            groups=self._merge_list(list1=self.current_user.groups_created,list2=self.current_user.joined_groups)

            if not groups :
                print("you have not any group in your account")
                return

            print("\n========== Send Group Message ==========")

            group = self._select_group(groups=groups,title="Choose a group")
                
            
            if group is None:
                print("group not found")
                return

            print(f"\n--- Group: {group.name} ---")
            print("Write 'exit' to leave the group chat.")
            print("Write 'change' to change group.")
            print("---------------------------")

        
            group_history = self.controller.get_group_chat(group.id)
            if group_history:
                print("\n[Previous Messages]")
                self._print_chat(group_history)
                print("-------------------\n")

            else:
                print("There are no messages in this group.")

            while True:
                content = input(f"{self.current_user.username}: ").strip()

                if content.lower() == "exit":
                    print("Group chat closed.")
                    break

                if content.lower() == "change":
                    new_group = self._select_group(users=groups,title="Who do you want to message?")
                        
                    if new_group is not None:
                        group = new_group
                        print(f"\n--- Chat with {group.name} ---")
                    
           
                        chat_history = self.controller.get_group_chat(group.id)
                        if chat_history:
                            print("\n[Previous Messages]")
                            self._print_chat(chat_history) 
                            print("-------------------\n")
                            continue
                        else:
                            print("There are no messages in this group.")

                if not content:
                    print("Message cannot be empty.")
                    continue

                try:
                    self.controller.send_message_to_group(
                        group_id=group.id,
                        sender_id=self.current_user.id,
                        content=content
                    )
                except Exception as e:
                    print(f"Message could not be sent: {e}")

        def show_group_chat(self) -> None:

            if not self._require_login():
                return

            member_groups = [
                group
                for group in self.controller.groups
                if self.current_user in group.members
            ]

            if not member_groups:
                print("You are not a member of any group.")
                return

            print("\n========== Group Chat ==========")

            group = self._select_group(groups=member_groups,title="Choose a group")
    
            if group is None:
                print("group not found")
                return

            
            chat = self.controller.get_group_chat(group.id)

            if chat :
                print(f"\n========== {group.name} ==========")
                self._print_chat(chat)
            else:
                print("There is no history of this in this group.")

           

        # -------------------- Helper Methods --------------------

        def _require_login(self) -> bool:

            if self.current_user is None:
                print("Please login first.")
                return False

            return True

        def _get_other_logged_in_users(self) -> list[User]:

            if self.current_user is None:
                return []

            return [
                user
                for user in self.login_users
                if user.id != self.current_user.id
            ]

        def _select_user(self,users: list[User],title: str) -> Optional[User]:
            
            if not users:
                print("No users are available.")
                return None

            print(f"\n{title}:")

            for index, user in enumerate(users, start=1):
                    print(f"{index}. {user.username}")

            try:
                choice = int(input("Choose user: ").strip())

                if choice < 1 or choice > len(users):
                    print("Invalid choice.")
                    return None

                return users[choice - 1]

            except ValueError:
                print("Please enter a number.")
                return None

        def _select_group(
            self,
            groups: list[Group],
            title: str
        ) -> Optional[Group]:

            if not groups:
                print("No groups are available.")
                return None

            print(f"\n{title}:")

            for index, group in enumerate(groups, start=1):
                print(f"{index}. {group.name}")

            try:
                choice = int(input("Choose group: ").strip())

                if choice < 1 or choice > len(groups):
                    print("Invalid choice.")
                    return None

                return groups[choice - 1]

            except ValueError:
                print("Please enter a number.")
                return None

        @staticmethod
        def _print_chat(chat: list[dict]) -> None:

            if not chat:
                print("No messages found.")
                return

            for item in chat:
                username = item.get("username", "Unknown")
                message = item.get("message", "")
                print(f"{username}: {message}")


        def _merge_list(self,list1: list[Group], list2: list[Group]):
            merge_list = []
            seen_ids = set()

            for group in list1 + list2:
                if group.id not in seen_ids:
                    merge_list.append(group)
                    seen_ids.add(group.id)

            return merge_list
        

        

        
        
             

            

          

            





            

    
