from typing import List


class TempmailException(Exception):
    pass


class ResponseException(TempmailException):
    def __init__(self, error_message: str):
        super().__init__(f'Response error: {error_message}')


class InvalidEmail(TempmailException):
    def __init__(self, email: str):
        super().__init__(f'Invalid email: {email}.')


class InvalidUsername(TempmailException):
    def __init__(self, username: str):
        super().__init__(f'Invalid username: {username}. Username must be in lower case.')


class InvalidDomain(TempmailException):
    def __init__(self, domain: str, domains: List[str]):
        super().__init__(f'Invalid domain: {domain}. Select one from following: {", ".join(domains)}.')


class MessageNotFound(TempmailException):
    def __init__(self, message_id: str):
        super().__init__(f'Message with id \'{message_id}\' not found.')


class TimeoutException(TempmailException):
    pass
