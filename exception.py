from dataclasses import dataclass


@dataclass
class BASE_EXCEPTION(Exception):
    message: str = ""
    status: int = None


class NETWORK_ERROR(BASE_EXCEPTION):
    pass


class LOCAL_ERROR(BASE_EXCEPTION):
    pass


class BAN_USER(LOCAL_ERROR):
    pass


@dataclass
class PROXY_ERROR(LOCAL_ERROR):
    message = "check your proxies"


@dataclass
class MAIN_PAGE_ERROR(LOCAL_ERROR):
    message = "not main page"
