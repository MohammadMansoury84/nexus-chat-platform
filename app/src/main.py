from fastapi import FastAPI
from src.api.GlobalExceptionHandler.global_exception_handler import GlobalExceptionHandler
from src.api.v1.router import main_router


def main():
    print("Hello from messenger-f3!")


app = FastAPI()
GlobalExceptionHandler(app=app)
app.include_router(
    main_router
)


if __name__ == "__main__":
    main()
