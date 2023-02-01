import rollbar
from app.core.config import EnvEnum


def init_rollbar(token: str, env: EnvEnum, **kwargs):
    if env == EnvEnum.production:
        rollbar.init(token, env.value, kwargs)