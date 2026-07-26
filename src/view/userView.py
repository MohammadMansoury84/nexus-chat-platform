from src.controllers.UserController import UserController
from src.models.User import User


class UserView():

        def __init__(self, controller: UserController)->None:
            self.controller = controller
            self.login_users :list[User]=[]
            self.current_user : User


        def show_Main_menu(self):

            while True:

                print("\n====== Messenger ======")
                print("1. Signup")
                print("2. Login")
                print("3. Send Message")
                print("4. Show Chat")
                print("5. Show Groups")
                print("6. Create Group")
                print("7. Add User to Group")
                print("8. Send Message to Group")
                print("9. Show Group Chat")
                print("10. Exit")

                choice = input("Enter your choice: ")

                try:
                    if choice == "1":
                        self.signup()
                    elif choice == "2":
                        self.login()
                    elif choice == "3":
                        self.send_message()
                    elif choice=="4":
                        self.change_user()
                    elif choice == "5":
                        self.show_groups()
                    elif choice == "6":
                        self.create_group()
                    elif choice == "7":
                        self.add_user_to_group()
                    elif choice == "8":
                        self.send_message_to_group()
                    elif choice == "9":
                        self.show_group_chat()
                    elif choice == "10":
                        print("Exiting...")
                        return

                except Exception as e:
                    print(f"Error: {e}")


        def signup(self):
            self.controller.signup(input("Username: "),input("Email: "),input("Password: "))


        def login(self)->None:
            user=self.controller.login(input("Username: "),input("Password: "))

            if (user is not None) and not(user in self.login_users):
                self.login_users.append(user)
                self.current_user=user
            else:
                print("login feild")
                return


        def send_message(self)->None:
    
            if self.current_user is None:
                print("Please login first.")
                return

            if len(self.login_users) <= 1:
                print("No other logged in users.")
                return

            print("Who do you want to message?")

            users = self._show_users

            for user in users:

                print(f"{len(users)}. {user.username}")
                        
        

            try:

                choice = int(input("\nChoose user: "))

                receiver = users[choice - 1]

            except (ValueError, IndexError):
                print("Invalid choice.")

            
            print("Write exit to leave ): ")

            while True:

                message = input("Message : ")

                if message.lower() == "exit":
                    break

            try:
                self.controller.send_message(sender_id=self.current_user.id,receiver_id=receiver.id,content=message)
                print("Message Sent.")
                    
                    
            except Exception as e:
                    print(e)
        

        def change_user(self):
            users=self._show_users()

            for user in users:
                print(f"{len(users)}. {user.username}")

            
            try:
                choice = int(input("\nChoose user: "))
                self.current_user = users[choice - 1]
                print(self.current_user)

            except (ValueError, IndexError):
                print("Invalid choice.")
            



            

        def _show_users(self)->list[User]:
            users = []
                
            for user in self.login_users:

                if user.id == self.current_user.id:
                    continue

                users.append(user)

            return users

        
        
            

            

          

            





            

    
