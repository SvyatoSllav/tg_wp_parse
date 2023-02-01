from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response
from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.db.session import scope
from uuid import uuid4
from typing import Callable


class SessionApiRoute(APIRoute):
    
    @inject
    def get_route_handler(self, session = Provide[Container.db]) -> Callable:
        original_route_handler = super().get_route_handler()

        async def preflight_handler(request: Request) -> Response:

            try:
                response = await original_route_handler(request)
                session.session.commit()
            finally:
                session.session.close()
        return preflight_handler
