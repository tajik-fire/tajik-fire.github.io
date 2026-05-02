import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    
    
    def __init__(self, app, storage=None):
        super().__init__(app)

        self.storage = storage or defaultdict(lambda: defaultdict(list))
        

        self.limits = {

            "POST /api/news": {"limit": 30, "window": 60},

            "POST /api/messenger/send": {"limit": 30, "window": 60},

            "POST /api/olympiads/submissions": {"limit": 30, "window": 60},

            "POST /api/auth/register": {"limit": 30, "window": 3600},

            "POST /api/auth/login": {"limit": 30, "window": 60},

            "POST /api/auth/reset-password-request": {"limit": 30, "window": 3600},

            "POST /api/comments": {"limit": 30, "window": 60},

            "POST /api/users/friends/request": {"limit": 30, "window": 60},
        }

    async def dispatch(self, request: Request, call_next):

        if request.url.path.startswith("/static") or request.url.path.startswith("/docs"):
            return await call_next(request)


        user_id = self._get_user_id(request)
        

        endpoint_key = f"{request.method} {request.url.path}"
        

        if endpoint_key in self.limits:
            limit_config = self.limits[endpoint_key]
            limit = limit_config["limit"]
            window = limit_config["window"]
            
            current_time = time.time()
            user_requests = self.storage[user_id][endpoint_key]
            

            user_requests[:] = [ts for ts in user_requests if current_time - ts < window]
            

            if len(user_requests) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Слишком много запросов. Попробуйте через {window // 60} мин."
                )
            

            user_requests.append(current_time)
        
        response = await call_next(request)
        return response

    def _get_user_id(self, request: Request) -> str:
        

        user = getattr(request.state, "user", None)
        if user and hasattr(user, "id"):
            return f"user:{user.id}"
        

        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"



from functools import wraps
import asyncio

def rate_limit(limit: int, window: int):
    
    requests_log = defaultdict(list)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):


            current_time = time.time()
            key = kwargs.get('user_id', 'default')
            

            requests_log[key] = [ts for ts in requests_log[key] if current_time - ts < window]
            
            if len(requests_log[key]) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Превышен лимит запросов"
                )
            
            requests_log[key].append(current_time)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
