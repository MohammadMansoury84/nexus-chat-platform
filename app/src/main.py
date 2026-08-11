
from fastapi import FastAPI
from src.api.GlobalExceptionHandler.global_exception_handler import GlobalExceptionHandler

def main():
    print("Hello from messenger-f3!")


    app=FastAPI()
    GlobalExceptionHandler(app=app)



if __name__ == "__main__":
    main()

