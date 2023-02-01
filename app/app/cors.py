from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable


class CORSHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def preflight_handler(request: Request) -> Response:
            if request.method == 'OPTIONS':
                response = Response()
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = '*'
                response.headers['Access-Control-Allow-Headers'] = '*'
            else:
                response = await original_route_handler(request)

        return preflight_handler
