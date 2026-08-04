

from src.entities.DTO.Request.AddUserToGroupRequest import AddUserToGroupRequest
from src.entities.DTO.Request.CreateGroupRequest import CreateGroupRequest
from src.entities.DTO.Request.GetChatRequest import GetChatRequest
from src.entities.DTO.Request.GetGroupChatRequest import GetGroupChatRequest
from src.entities.DTO.Request.LoginRequest import LoginRequest
from src.entities.DTO.Request.SendMessageTOGroupRequest import SendMessageToGroupRequest
from src.entities.DTO.Request.SendMessageToPrivateChatRequest import (
    SendMessageToPrivateChatRequest,
)
from src.entities.DTO.Request.SignupRequest import SignupRequest
from src.ServerNetwork.AsyncClient import AsyncClient
from uuid import UUID
from src.entities.RequestType import RequestType

import asyncio



class UserView:
    def __init__(self, client: AsyncClient) -> None:

        self._client = client
        self._current_user_id: UUID | None = None
        self._current_username: str | None = None
        self._active_private_user_id: UUID | None = None
        self._active_private_username: str | None = None
        self._client.set_event_callback(self._show_event)

    async def run(self) -> None:
        await self._client.connect()
        print("Connected to server.")

        try:
            while True:
                self._show_menu()
                choice = await self._input("Choose: ")

                try:
                    should_exit = await self._run_choice(choice)
                    if should_exit:
                        break
                except Exception as exc:
                    print(f"Error: {exc}")
        finally:
            await self._client.close()

    def _show_menu(self) -> None:
        print("\n========== Messenger ==========")
        print("1. Signup")
        print("2. Login")
        print("3. List users")
        print("4. Send private message")
        print("5. Show private chat")
        print("6. Create group")
        print("7. List groups")
        print("8. Add user to group")
        print("9. Send group message")
        print("10. Show group chat")
        print("11. Logout")
        print("12. Exit")

    async def _run_choice(self, choice: str) -> bool:
        actions = {
            "1": self._signup,
            "2": self._login,
            "3": self._list_users,
            "4": self._send_private_message,
            "5": self._show_private_chat,
            "6": self._create_group,
            "7": self._list_groups,
            "8": self._add_user_to_group,
            "9": self._send_group_message,
            "10": self._show_group_chat,
            "11": self._logout,
        }

        if choice == "12":
            return True

        action = actions.get(choice)
        if action is None:
            print("Invalid choice.")
            return False

        await action()
        return False

    async def _signup(self)->None:

        print("\n========== Signup ==========")

        dto = SignupRequest(
            username=await self._input("Username: "),
            email=await self._input("Email: "),
            password=await self._input("Password: "),
        )
        result = await self._client.send_request(RequestType.SINGUP, dto.model_dump())
        print(result)


    async def _login(self) -> None:
        print("\n========== Login ==========")
        if self._current_user_id is not None:
            print("You are already logged in.")
            return
        dto = LoginRequest(
            username=await self._input("Username: "),
            password=await self._input("Password: "),
        )
        result = await self._client.send_request(RequestType.LOGIN, dto.model_dump())
        if result.get("logged_in"):
            self._current_user_id = UUID(result["user"]["id"])
            self._current_username = result["user"]["username"]
        print(result)

    async def _logout(self) -> None:
        print("\n========== logout ==========")

        result = await self._client.send_request(RequestType.LOGOUT)
        self._current_user_id = None
        self._current_username = None
        print(result)



    async def _send_private_message(self) -> None:
        current_user_id = self._require_login()

        while True:
            selected_user = await self._select_user(
                title="Choose User For Private Chat"
            )

            if selected_user is None:
                return

            selected_user_id = UUID(selected_user["id"])
            selected_username = selected_user["username"]

        
            self._active_private_user_id = selected_user_id
            self._active_private_username = selected_username

            print(f"\n========== Chat with {selected_username} ==========")
            print("Type 'exit' to return to menu.")
            print("Type 'change' to choose another user.")

            await self._show_private_chat_history(selected_user)

            while True:
                content = await self._input(
                    f"{self._current_username}: "
                )

                command = content.strip().lower()

                if command == "exit":
                    self._active_private_user_id = None
                    self._active_private_username = None

                    print("Private chat closed.")
                    return

                if command == "change":
                    self._active_private_user_id = None
                    self._active_private_username = None

                    break

                if not content.strip():
                    print("Message cannot be empty.")
                    continue

                dto = SendMessageToPrivateChatRequest(
                    sender_id=current_user_id,
                    receiver_id=selected_user_id,
                    message_content=content,
                )

                result = await self._client.send_request(
                    RequestType.SEND_PRIVATE_MESSAGE,
                    dto.model_dump(),
                )

                if not result.get("delivered", True):
                    print(
                        f"{selected_username} is currently offline. "
                        "The message was saved."
                    )

    async def _list_users(self) -> None:
        self._require_login()

        result = await self._client.send_request(
        RequestType.GET_ALL_USERS_FOR_SHOW_USERS
        )

        users = result.get("users", [])

        if not users:
            print(
                result.get(
                    "message",
                    "No other users are logged in.",
                )
            )
            return

        print("\n========== Logged-in Users ==========")

        for index, user in enumerate(users, start=1):
            print(f"{index}. {user['username']}")



    async def _show_private_chat(self) -> None:
        current_user_id = self._require_login()

        selected_user = await self._select_user(
            title="Choose User For Private Chat"
        )

        if selected_user is None:
            return

        dto = GetChatRequest(
            user1_id=current_user_id,
            user2_id=UUID(selected_user["id"]),
        )

        result = await self._client.send_request(
            RequestType.GET_PRIVATE_CHAT,
            dto.model_dump()
        )

        chat = result.get("chat", [])

        if not chat:
            print(
                f"You have no chat history with "
                f"{selected_user['username']}."
            )
            return

        print(
            f"\n========== Chat with "
            f"{selected_user['username']} =========="
        )

        for item in chat:
            username = item.get("username", "Unknown")
            message = item.get("message", "")

            print(f"{username}: {message}")


    async def _list_groups(self) -> None:
        
        result = await self._client.send_request(RequestType.GET_ALL_GROUPS_FOR_SHOW_USERS)
        groups=result.get("groups",[])
        if not groups:
            print(
                result.get("message","You are not a member or creator of any group.")
                )
            return
        print("\n========== groups ==========")

        for index, group in enumerate(groups, start=1):
            print(f"{index}. {group['name']}")

            




    async def _create_group(self) -> None:
        print("\n========== Create Group ==========")
        user_id = self._require_login()
        dto = CreateGroupRequest(
            group_name=await self._input("Group name: "),
            creator_id=user_id,
        )
        print(await self._client.send_request(RequestType.CREATE_GROUP, dto.model_dump()))


    async def _add_user_to_group(self) -> None:
        print("\n========== Add User To Group ==========")

        creator_id = self._require_login()

        selected_group = await self._select_group(
            title="Choose Group"
        )

        if selected_group is None:
            return

        selected_user = await self._select_user(
            title="Choose User To Add"
        )

        if selected_user is None:
            return

        dto = AddUserToGroupRequest(
            group_id=UUID(selected_group["id"]),
            creator_id=creator_id,
            user_id=UUID(selected_user["id"]),
        )

        result = await self._client.send_request(
            RequestType.ADD_USER_TO_GROUP,
            dto.model_dump(),
        )

        print(
            result.get(
                "message",
                "User added to group successfully.",
            )
        )


    async def _send_group_message(self) -> None:
        print("\n=========send group message===========")
        user_id = self._require_login()
        dto = SendMessageToGroupRequest(
            group_id=UUID(await self._input("Group UUID: ")),
            sender_id=user_id,
            message_content=await self._input("Message: "),
        )
        print(await self._client.send_request(RequestType.SEND_MESSAGE_TO_GROUP, dto))

        
    async def _show_group_chat(self) -> None:
        print("\n=========show group chat===========")
        self._require_login()
        dto = GetGroupChatRequest(
            group_id=UUID(await self._input("Group UUID: ")),
        )
        result = await self._client.send_request(RequestType.GET_GROUP_CHAT, dto)
        if result :
            print(result)
        else:
            print("There is no history of this in this group.")


    async def _show_event(self, message: dict) -> None:
        event = message.get("event")
        data = message.get("data", {})

        if event == "private_message":
            sender_id_text = data.get("sender_id")

            sender_username = data.get(
                "sender_username",
                "Unknown",
            )

            content = data.get(
                "content",
                "",
            )

            try:
                sender_id = UUID(sender_id_text)
            except (ValueError, TypeError):
                sender_id = None

            
            if sender_id == self._active_private_user_id:

                print(
                    f"\n{sender_username}: {content}"
                )

      
            else:
                print(
                    f"\n[New private message from "
                    f"{sender_username}] {content}"
                )

                print(
                    "Choose 'Send private message' "
                    "to open the conversation."
                )

            return


        if event == "group_message":
            print(
                f"\n[Group {data.get('group_id')}] "
                f"{data.get('sender_username')}: "
                f"{data.get('content')}"
            )
            return


        if event == "added_to_group":
            print(
                f"\nYou were added to group "
                f"{data.get('group_name')}"
            )

    @staticmethod
    async def _input(prompt: str) -> str:
        return (await asyncio.to_thread(input, prompt)).strip()

    async def _select_user(
        self,
        title: str,
        ) -> dict | None:
        result = await self._client.send_request(
            RequestType.GET_ALL_USERS_FOR_SHOW_USERS
        )

        users = result.get("users", [])

        if not users:
            print(
                result.get(
                    "message",
                    "No other users are available.",
                )
            )
            return None

        print(f"\n========== {title} ==========")

        for index, user in enumerate(users, start=1):
            print(f"{index}. {user['username']}")

        choice_text = await self._input("Choose user: ")

        try:
            choice = int(choice_text)
        except ValueError:
            print("Please enter a number.")
            return None

        if choice < 1 or choice > len(users):
            print("Invalid user selection.")
            return None

        return users[choice - 1]


    async def _select_group(self, title: str) -> dict | None:
        result = await self._client.send_request(
            RequestType.GET_ALL_GROUPS_FOR_SHOW_USERS
        )

        groups = result.get("groups", [])

        if not groups:
            print(
                result.get(
                    "message",
                    "You have not created any groups.",
                )
            )
            return None

        print(f"\n========== {title} ==========")

        for index, group in enumerate(groups, start=1):
            print(f"{index}. {group['name']}")

        

        while True:
            choice_text = await self._input("Choose group: ")

            try:
                choice = int(choice_text)
            except ValueError:
                print("Please enter a number.")
                continue

            if choice == 0:
                return None

            if choice < 1 or choice > len(groups):
                print("Invalid group selection.")
                continue

            return groups[choice - 1]

    async def _show_private_chat_history(
        self,
        selected_user: dict,
    ) -> None:
        current_user_id = self._require_login()

        dto = GetChatRequest(
            user1_id=current_user_id,
            user2_id=UUID(selected_user["id"]),
        )

        result = await self._client.send_request(
            RequestType.GET_PRIVATE_CHAT,
            dto.model_dump(),
        )

        chat = result.get("chat", [])

        if not chat:
            print(
                f"You have no chat history with "
                f"{selected_user['username']}."
            )
            return

        print("\n========== Previous Messages ==========")

        for item in chat:
            username = item.get("username", "Unknown")
            message = item.get("message", "")

            print(f"{username}: {message}")

        print("=======================================")


    def _require_login(self) -> UUID:
        if self._current_user_id is None:
            raise RuntimeError("Please login first.")
        return self._current_user_id









    # def show_groups(self) -> None:
    #     if not self._require_login():
    #         return

    #     print("\n========== Groups ==========")

    #     groups = self.current_user.joined_groups

    #     if not groups:
    #         print("No groups have been found.")
    #         return

    #     for index, group in enumerate(groups, start=1):
    #         print(f"{index}. {group.name}")
    # def change_user(self) -> None:
    #     if not self._require_login():
    #         return

    #     if not self.login_users:
    #         print("No logged-in users.")
    #         return

    #     print("\n========== Change User ==========")

    #     users = self._get_other_logged_in_users()

    #     if users:
    #         user = self._select_user(users=users, title="Choose current user")

    #         if user is None:
    #             print("user not found")
    #             return

    #         self.current_user = user
    #         print(f"Current user changed to {user.username}.")
    #     else:
    #         print("No other logged-in users are available.")




    # def show_logged_in_users(self) -> None:
    #     if not self._require_login():
    #         return

    #     if not self.login_users:
    #         print("No logged-in users.")
    #         return

    #     print("\n========== Logged-in Users ==========")

    #     for index, user in enumerate(self.login_users, start=1):
    #         current_sign = ""

    #         if self.current_user is not None:
    #             if user.id == self.current_user.id:
    #                 current_sign = " <- Current User"

    #         print(f"{index}. {user.username}{current_sign}")



        # def add_user_to_group(self) -> None:

    #     print("\n========== Add User to Group ==========")

    #     group = self._select_group(
    #         groups=self.current_user.groups_created, title="Choose a group"
    #     )

    #     if group is None:
    #         print("group not found")
    #         return

    #     available_users = []

    #     for user in self.login_users:
    #         is_not_member = True

    #         for member in group.members:
    #             if member.id == user.id:
    #                 is_not_member = False
    #                 break

    #         if is_not_member:
    #             available_users.append(user)

    #     if not available_users:
    #         print("All registered users are already members of this group.")
    #         return

    #     user = self._select_user(users=available_users, title="Choose a user to add")

    #     if user is None:
    #         print("user not found")
    #         return



        # def send_message_to_group(self) -> None:

    #     if not self._require_login():
    #         return

    #     groups = self._merge_list(
    #         list1=self.current_user.groups_created, list2=self.current_user.joined_groups
    #     )

    #     if not groups:
    #         print("you have not any group in your account")
    #         return

    #     print("\n========== Send Group Message ==========")

    #     group = self._select_group(groups=groups, title="Choose a group")

    #     if group is None:
    #         print("group not found")
    #         return

    #     print(f"\n--- Group: {group.name} ---")
    #     print("Write 'exit' to leave the group chat.")
    #     print("Write 'change' to change group.")
    #     print("---------------------------")

    #     group_history = self._group_controller.get_group_chat(group.id)
    #     if group_history:
    #         print("\n[Previous Messages]")
    #         self._print_chat(group_history)
    #         print("-------------------\n")

    #     else:
    #         print("There are no messages in this group.")

    #     while True:
    #         content = input(f"{self.current_user.username}: ").strip()

    #         if content.lower() == "exit":
    #             print("Group chat closed.")
    #             break

    #         if content.lower() == "change":
    #             new_group = self._select_group(
    #                 users=groups, title="Who do you want to message?"
    #             )

    #             if new_group is not None:
    #                 group = new_group
    #                 print(f"\n--- Chat with {group.name} ---")

    #                 chat_history = self._group_controller.get_group_chat(group.id)
    #                 if chat_history:
    #                     print("\n[Previous Messages]")
    #                     self._print_chat(chat_history)
    #                     print("-------------------\n")
    #                     continue
    #                 print("There are no messages in this group.")

    #         if not content:
    #             print("Message cannot be empty.")
    #             continue

    #         try:
    #             self._group_controller.send_message_to_group(
    #                 group_id=group.id, sender_id=self.current_user.id, content=content
    #             )

    #         except Exception as e:
    #             print(f"Message could not be sent: {e}")




        # def show_group_chat(self) -> None:

    #     if not self._require_login():
    #         return

    #     member_groups = [
    #         group
    #         for group in self._group_controller.get_all_groups()
    #         if self.current_user in group.members
    #     ]

    #     if not member_groups:
    #         print("You are not a member of any group.")
    #         return

    #     print("\n========== Group Chat ==========")

    #     group = self._select_group(groups=member_groups, title="Choose a group")

    #     if group is None:
    #         print("group not found")
    #         return

    #     chat = self._group_controller.get_group_chat(group.id)

    #     if chat:
    #         print(f"\n========== {group.name} ==========")
    #         self._print_chat(chat)
    #     else:
    #         print("There is no history of this in this group.")



        # def _require_login(self) -> bool:

    #     if self.current_user is None:
    #         print("Please login first.")
    #         return False

    #     return True

    # def _get_other_logged_in_users(self) -> list[User]:

    #     if self.current_user is None:
    #         return []

    #     return [user for user in self.login_users if user.id != self.current_user.id]

    # def _select_user(self, users: list[User], title: str) -> User | None:

    #     if not users:
    #         print("No users are available.")
    #         return None

    #     print(f"\n{title}:")

    #     for index, user in enumerate(users, start=1):
    #         print(f"{index}. {user.username}")

    #     try:
    #         choice = int(input("Choose user: ").strip())

    #         if choice < 1 or choice > len(users):
    #             print("Invalid choice.")
    #             return None

    #         return users[choice - 1]

    #     except ValueError:
    #         print("Please enter a number.")
    #         return None

    # def _select_group(self, groups: list[Group], title: str) -> Group | None:

    #     if not groups:
    #         print("No groups are available.")
    #         return None

    #     print(f"\n{title}:")

    #     for index, group in enumerate(groups, start=1):
    #         print(f"{index}. {group.name}")

    #     try:
    #         choice = int(input("Choose group: ").strip())

    #         if choice < 1 or choice > len(groups):
    #             print("Invalid choice.")
    #             return None

    #         return groups[choice - 1]

    #     except ValueError:
    #         print("Please enter a number.")
    #         return None

    # @staticmethod
    # def _print_chat(chat: list[dict]) -> None:

    #     if not chat:
    #         print("No messages found.")
    #         return

    #     for item in chat:
    #         username = item.get("username", "Unknown")
    #         message = item.get("message", "")
    #         print(f"{username}: {message}")

    # def _merge_list(self, list1: list[Group], list2: list[Group]):
    #     merge_list = []
    #     seen_ids = set()

    #     for group in list1 + list2:
    #         if group.id not in seen_ids:
    #             merge_list.append(group)
    #             seen_ids.add(group.id)

    #     return merge_list


