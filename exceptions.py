

class BasicException(Exception):
    """Generic app exception"""
    pass


class ProxiesPoolIsemptyExeption(BasicException):
    pass


class ResponseRedirectException(BasicException):
    pass


class ParserConfigIsEmptyException(BasicException):
    pass
