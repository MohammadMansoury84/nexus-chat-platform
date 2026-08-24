from src.api.dependencies.websocket_dependency import get_connection_manager
from src.infrastructure.websocket.realtime_publisher import RealTimePublisher


def get_realtime_publisher() -> RealTimePublisher:
    return RealTimePublisher(
        connection_manager=get_connection_manager(),
    )
