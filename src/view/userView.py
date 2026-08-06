

from src.entities.DTO.Request.AddUserToGroupRequest import AddUserToGroupRequest
from src.entities.DTO.Request.CreateGroupRequest import CreateGroupRequest
from src.entities.DTO.Request.GetChatRequest import GetChatRequest
from src.entities.DTO.Request.GetGroupChatRequest import GetGroupChatRequest
from src.entities.DTO.Request.LoginRequest import LoginRequest
from src.entities.DTO.Request.SendMessageTOGroupRequest import SendMessageToGroupRequest
from src.entities.DTO.Request.SendMessageToPrivateChatRequest import (
    SendMessageToPrivateChatRequest,
)
from src.entities.DTO.Request.DeleteGroupByIdRequest import DeleteGroupByIdRequest
from src.entities.DTO.Request.ShowGroupMembersRequest import ShowGroupMembersRequest
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

        self._active_group_id :UUID | None = None
        self._active_group_name:str | None = None

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
        print("11. delete group")
        print("12. show group members")
        print("13. Logout")


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
            "11":self.delete_group,
            "12":self.show_group_members,
            "13": self._logout,
        }

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

                    await self._client.send_request(
                        request_type=RequestType.LEAVE_PRIVATE_CHAT,
                        data=
                        {
                            "other_user_id": str(selected_user_id)
                        }
                    )

                    self._active_private_user_id = None
                    self._active_private_username = None



                    print("Private chat closed.")
                    return

                if command == "change":

                    await self._client.send_request(
                        request_type=RequestType.LEAVE_PRIVATE_CHAT,
                        data=
                        {
                            "other_user_id": str(selected_user_id)
                        }
                    )

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

                await self._client.send_request(
                    RequestType.SEND_PRIVATE_MESSAGE,
                    dto.model_dump(),
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
        self._require_login()

        selected_user = await self._select_user(
            "Choose user for show Private Chat"
        )

        if selected_user is None:
            return

        await self._show_private_chat_history(
            selected_user
    )
    

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
        current_user_id=self._require_login()
        print("\n=========send group message===========")
        while True:
            selected_group=await self._select_group(title="Choose group For Chat")
            if selected_group is None:
                return
            
            selected_group_id=UUID(selected_group["id"])
            selected_group_name=selected_group["name"]

            self._active_group_id=selected_group_id
            self._active_group_name=selected_group_name

            print(f"\n========== group Chat {selected_group_name} ==========")
            print("Type 'exit' to return to menu.")
            print("Type 'change' to choose another group.")
            print("Type 'members' to see group members.")

            await self._show_group_chat_history(selected_group)

            while True:

                print(
                    f"{self._current_username}: ",
                    end="",
                    flush=True
                )

                content = await self._input("")

                command = content.strip().lower()


                if command == "exit":

                    await self._client.send_request(
                        request_type=RequestType.LEAVE_GROUP_CHAT,
                        data={"group_id":selected_group_id},
                    )



                    self._active_group_id = None
                    self._active_group_name = None

                    print("group chat closed.")
                    return

                if command == "change":

                    await self._client.send_request(
                        request_type=RequestType.LEAVE_GROUP_CHAT,
                        data={"group_id":selected_group_id},
                    )

                    self._active_group_id = None
                    self._active_group_name = None

                    break

                if command == "members":
                    await self._show_members(user_id=self._current_user_id,group_id=self._active_group_id)
                    return


                if not content.strip():
                    print("Message cannot be empty.")
                    continue

                dto=SendMessageToGroupRequest(
                    sender_id=current_user_id,
                    group_id=selected_group_id,
                    message_content=content
                )

                await self._client.send_request(RequestType.SEND_MESSAGE_TO_GROUP,dto.model_dump())


    async def delete_group(self) -> None:

        self._require_login()

        print("\n========= Delete Group =========")

        selected_group = await self._select_group(
            "Choose group to delete"
        )

        if selected_group is None:
            return

        dto = DeleteGroupByIdRequest(
            group_id=UUID(selected_group["id"])
        )

        result = await self._client.send_request(
            RequestType.DELETE_GROUP_BY_ID,
            dto.model_dump()
        )

        print(
            result.get(
                "message",
                "Group deleted."
            )
        )

    async def show_group_members(self)->None:
        group=await self._select_group("Choose group for show group member") 
        if group is not None:
            dto=ShowGroupMembersRequest(user_id=self._current_user_id,group_id=group.get("id"))
            result=await self._client.send_request(RequestType.SHOW_GROUP_MEMBER,dto.model_dump())
            members = result.get("users", [])
            for index, member in enumerate(members, start=1):
                print(f"{index}. {member['username']}")

    async def _show_members(self,user_id:UUID,group_id):

        dto=ShowGroupMembersRequest(user_id=user_id,group_id=group_id)
        result=await self._client.send_request(RequestType.SHOW_GROUP_MEMBER,dto.model_dump())
        members = result.get("users", [])
        for index, member in enumerate(members, start=1):
            print(f"{index}. {member['username']}")





                
    async def _show_group_chat(self) -> None:
        self._require_login()
        selected_group= await self._select_group("Choose group for show group Chat")
        if selected_group is None:
            return
        await self._show_group_chat_history(selected_group=selected_group)
        


    async def _show_event(self, message: dict) -> None:
        event = message.get("event")
        data = message.get("data", {})

        content = data.get(
                "content",
                "")

        sender_username = data.get(
                "sender_username",
                "Unknown",
            )


        if event == "private_message":

            sender_id_text = data.get("sender_id")

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
                    f"{sender_username}]: {content}"
                )

                print(
                    "Choose 'Send private message' "
                    "to open the conversation."
                )

            return


        if event == "group_message":

            group_id_text = data.get("group_id")
            try:
                group_id = UUID(group_id_text)
            except (ValueError, TypeError):
                group_id = None

            if group_id==self._active_group_id:
                
                print(
                    f"\n{sender_username}: {content}"
                )
            else:
                print(
                    f"\n[New group message from "
                    f"{sender_username}]: {content}"
                )

                print(
                    "Choose 'Send group message' "
                    "to open the conversation."
                )
                

            return


        if event == "added_to_group":
            print(
                f"\nYou were added to group "
                f"{data.get('group_name')}"
            )

            return
        

        if event == "delete_group":
            print(
                f"\n group was deleted "
                f"{data.get('group_name')}"
            )
            return
        

        if event == "exit_private_chat":
            user_id_text = data.get("user_id")

            try:
                user_id = UUID(user_id_text)
            except (ValueError, TypeError):
                user_id = None


            if user_id == self._active_private_user_id:
                print(
                    f"\n {data.get("username")} exit chat "
                )

            return
        

        if event =="exit_group_chat":

            group_id_text = data.get("group_id")

            try:
                group_id = UUID(group_id_text)
            except (ValueError, TypeError):
                group_id = None

            if group_id==self._active_group_id:

                print(
                    f"\n {data.get("username")} exit group chat "
                )

                return

    

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


    async def _show_group_chat_history(self,selected_group:dict)->None:
        self._require_login()
        dto=GetGroupChatRequest(
            group_id=UUID(selected_group["id"])
        )

        result=await self._client.send_request(
            RequestType.GET_GROUP_CHAT,
            dto.model_dump(),
        )

        chat = result.get("chat", [])

        
        if not chat:
            print(
                f"group have no chat history "
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
