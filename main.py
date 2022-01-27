from datetime import datetime

from fastapi import Body, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis import StrictRedis
from starlette.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                              HTTP_422_UNPROCESSABLE_ENTITY)

from config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from db import RedisDatabaseProxy
from schemas import VisitedLinksIn

app = FastAPI()
db = StrictRedis(REDIS_HOST, REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, charset="utf-8", decode_responses=True)
db_proxy = RedisDatabaseProxy(database=db)

STATUS_OK = {'status': 'ok'}

@app.exception_handler(Exception)
def exception_handler_view(request: Request, exception: Exception, status = None, status_code = HTTP_400_BAD_REQUEST):
    """
        Улавливает ошибки и возвращает информацию о них
    """
    if status is None:
        status = exception.args[0] if len(exception.args) > 0 else "error"
    return JSONResponse({"status": status}, status_code=status_code)


@app.exception_handler(RequestValidationError)
def request_validation_error_handler(request: Request, exception: RequestValidationError):
    """
        Перезаписывает уже существующий handler, чтобы все были в одном формате
    """
    error = exception.errors()[0]
    return exception_handler_view(request, exception, status = error.get('msg'), status_code = HTTP_422_UNPROCESSABLE_ENTITY)
    

@app.post("/visited_links")
def add_visited_links_view(visited_links_instance: VisitedLinksIn = Body(...)):
    unix_now = datetime.utcnow().strftime("%s")
    db_proxy.add_values_in_set(unix_now, *visited_links_instance.links)
    return STATUS_OK


@app.get('/visited_domains')
def get_visited_domains_view(start: str = Query("", alias='from'), end: str = Query("", alias='to')):
    try:
        a, b = (int(start), int(end))
    except ValueError:
        raise ValueError("ValueError: 'from' and 'to' must be Integers only! (unix timestamp)")

    if not a < b: raise ValueError("ValueError: 'from' must be less than 'to'")

    domains = db_proxy.get_unique_values_by_timerange(start = a, end = b)

    return {
        "domains": list(domains),
        **STATUS_OK
    }

