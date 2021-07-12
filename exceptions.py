class BasicException(Exception):
    """Generic app exception"""
    pass


class BookDownloadLinkNotFound(BasicException):
    pass


class ResponseRedirectException(BasicException):
    pass
