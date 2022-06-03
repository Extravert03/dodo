import asyncio
from typing import Iterable, NamedTuple

import httpx

from . import requests
from .utils import exceptions

__all__ = (
    'run_requests',
    'run_request',
)


class DodoAPIResponse(NamedTuple):
    request: requests.DodoAPIRequest
    html: str
    content: bytes


async def run_request(cookies: dict, request: requests.DodoAPIRequest,
                      times: int = 3) -> DodoAPIResponse:
    headers = {
        'User-Agent': 'Goretsky-Band'
    }
    async with httpx.AsyncClient(cookies=cookies) as client:
        request_params = request.get_request_params()
        try:
            response = await client.request(**request_params, headers=headers)
        except httpx.HTTPError:
            if times <= 0:
                raise exceptions.UnsuccessfulRequestError
            return await run_request(cookies, request, times - 1)
        return DodoAPIResponse(request=request, html=response.text, content=response.content)


async def run_requests(
        cookies: dict,
        executable_requests: Iterable[requests.DodoAPIRequest]
) -> tuple[DodoAPIResponse, ...]:
    tasks = [run_request(cookies, request) for request in executable_requests]
    return await asyncio.gather(*tasks)
