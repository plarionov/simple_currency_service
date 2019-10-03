from aiohttp import web, BasicAuth
from aiohttp.web_middlewares import middleware

from constants import AUTH_DICT


def check_access(
        auth_dict: dict,
        header_value: str) -> bool:

    auth = BasicAuth.decode(header_value)

    if auth.login not in auth_dict:
        return False
    if auth.password != auth_dict.get(auth.login):
        return False

    return True


@middleware
async def basic_auth(request, handler) -> web.Response:
    if 'Authorization' not in request.headers:
        raise web.HTTPUnauthorized()
    if not check_access(AUTH_DICT, request.headers['Authorization']):
        raise web.HTTPUnauthorized(headers={'WWW-Authenticate': 'Basic'})

    return await handler(request)
