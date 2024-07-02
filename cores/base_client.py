# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import asyncio
import copy
from loguru import logger
import requests
import urllib3

from commons.decorators import retry_on_exceptions
from config import settings


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# from aiohttp.http_parser import HeadersParser


# def monkey_init(
#     self,
#     max_line_size: int = 81900,
#     max_headers: int = 32768,
#     max_field_size: int = 81900,
# ) -> None:
#     self.max_line_size = max_line_size
#     self.max_headers = max_headers
#     # self.max_field_size = max_field_size
#     self.max_field_size = 2 << 31


# HeadersParser.__init__ = monkey_init
import aiohttp


class BaseClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.timeout = 30
        self.echo_request_details = False

    def _request(self, method, url, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        response = self.session.request(method, url, **kwargs)
        response.encoding = response.apparent_encoding
        if self.echo_request_details:
            logger.debug(
                'fetch info: {}'.format(
                    {
                        "method": method,
                        "url": response.request.url,
                        "headers": response.request.headers,
                        "cookies": self.cookies,
                        "params": kwargs.get('params'),
                        "data": kwargs.get('data'),
                        "json": kwargs.get('json'),
                        "status": response.status_code,
                        "encode": response.apparent_encoding,
                        "cost(s)": response.elapsed.seconds,
                        "text": response.text,
                    }
                ),
            )
        else:
            logger.info(
                'fetch info: {}'.format(
                    {
                        "method": method,
                        "url": response.request.url,
                        # "headers": response.request.headers,
                        # "cookies": self.cookies,
                        "status": response.status_code,
                        "encode": response.apparent_encoding,
                        "cost(s)": response.elapsed.seconds,
                        # "text": response.text,
                    }
                ),
            )

        return response.text

    # def post(self, url, **kwargs):
    #     response = self.session.post(url, **kwargs)
    #     return response.text

    @property
    def cookies(self):
        cookies = self.session.cookies.get_dict()
        return cookies

    @cookies.setter
    def cookies(self, cookies):
        if not cookies:
            return
        if isinstance(cookies, dict):
            self.session.cookies.update(cookies)
        if isinstance(cookies, list):
            for cookie in cookies:
                self.session.cookies.update(cookie)

    @property
    def proxies(self):
        proxies = self.session.proxies
        return proxies

    @proxies.setter
    def proxies(self, proxy):
        proxies = {"http": proxy, "https": proxy}
        self.session.proxies = proxies


class BaseAsyncClient:
    def __init__(self):
        # self.session = aiohttp.ClientSession()
        self.timeout = 30
        self.echo_request_details = settings.ECHO_REQUEST_DETAILS
        # self._cookies = None
        self._cookie_jar = aiohttp.CookieJar(unsafe=True)
        self._proxies = None
        self.verify = False
        self.curr_content_type = None
        self.append_headers = {}

    @property
    def default_headers(self):
        raise NotImplementedError

    @property
    def content_type_is_text(self):
        result = True
        if getattr(self, 'curr_content_type', None):
            if self.curr_content_type.startswith('image/'):
                result = False
        return result

    @retry_on_exceptions(exceptions=[asyncio.exceptions.TimeoutError, aiohttp.client_exceptions.ClientConnectorError])
    async def _request(self, method, url, **kwargs):
        timeout = kwargs.pop('timeout', self.timeout)
        aio_session = None
        try:
            '''
            错误：
                E   aiohttp.http_exceptions.LineTooLong: 400, message:
                E     Got more than 8190 bytes (11984) when reading Header value is too long.

                aiohttp/_http_parser.pyx:732: LineTooLong
            解决：
                max_line_size=81900,
                max_field_size=81900,
            '''
            headers = kwargs.pop('headers', self.default_headers)
            if self.append_headers:
                headers.update(self.append_headers)

            async with aiohttp.ClientSession(
                # cookies=self._cookies,
                cookie_jar=self._cookie_jar,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers=headers,
                max_line_size=81900,
                max_field_size=81900,
            ) as session:
                aio_session = session
                logger.debug(self._proxies)
                if 'proxy' not in kwargs and self._proxies:
                    kwargs['proxy'] = self._proxies
                if 'ssl' not in kwargs and self.verify is not None:
                    kwargs['ssl'] = self.verify
                async with session.request(method, url, timeout=timeout, **kwargs) as response:
                    # 获取Content-Type头
                    self.curr_content_type = response.headers.get('Content-Type', '').lower()
                    if self.content_type_is_text:
                        response_text = await response.text()
                    else:
                        response_text = await response.read()

                    response_encoding = response.get_encoding()

                    log_info = {
                        "method": method,
                        "url": str(response.request_info.url),
                        "status": response.status,
                        "encode": response_encoding,
                    }
                    if self.echo_request_details:
                        log_info.update(
                            dict(
                                {
                                    "request-headers": dict(response.request_info.headers),
                                    "response-headers": dict(response.headers),
                                    "response-text": (
                                        response_text
                                        if self.content_type_is_text
                                        else f"返回内容({self.curr_content_type})不是纯文本"
                                    ),
                                },
                                **kwargs,
                            )
                        )
                    logger.info(log_info)

                    await aio_session.close()
                    aio_session = None
                    return response_text
        except Exception as e:
            # logger.exception(f"An unexpected error occurred: {e}")
            raise e
        finally:
            if aio_session:
                await aio_session.close()

    @property
    def cookies(self):
        return self._cookie_jar

    @cookies.setter
    def cookies(self, cookies):
        if not cookies:
            return
        if isinstance(cookies, dict):
            if '' in cookies.keys():
                del cookies['']
            self._cookie_jar.update_cookies(cookies)
        elif isinstance(cookies, list):
            tmp = {}
            for cookie in cookies:
                if '' == cookie['name']:
                    continue
                # logger.debug(cookie['name'], cookie['value'])
                tmp[cookie['name']] = cookie['value']
            # self._cookies = tmp
            # self._cookie_jar = aiohttp.CookieJar(unsafe=True)
            self._cookie_jar.update_cookies(tmp)

    @property
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, proxy):
        self._proxies = proxy

    async def clean(self):
        self._cookies = None


class CommonClient(BaseAsyncClient):
    def __init__(self):
        super().__init__()

    @property
    def default_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }

    def post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)
