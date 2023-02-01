from fastapi import Depends
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from dependency_injector.wiring import inject, Provide
from starlette.requests import Request
from starlette.responses import Response
from app.core.containers import Container
from app.db.session import scope
from uuid import uuid4


class AddSessionMiddleware(BaseHTTPMiddleware):
    
    @inject
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint, db = Provide[Container.db]) -> Response:
        scope.set(str(uuid4()))
        try:
            response = await call_next(request)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()
            db.session.remove()
            
        return response
