from hashlib import md5
from json import JSONDecodeError
from random import choice
from time import sleep
from typing import List, Union

import requests
from random_username.generate import generate_username

from tempmail import exceptions


class Tempmail:
    def __init__(self, username: str = None, email: str = None):
        self.domains = self.get_domains()
        self._email, self._email_hash = None, None

        if email is not None:
            self.email = email
        elif username is not None:
            self.email = username + choice(self.domains)
        else:
            self.email = generate_username()[0].lower() + choice(self.domains)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str):
        if '@' not in email:
            raise exceptions.InvalidEmail(email)

        username, domain = email.split("@", 1)

        if (domain := f'@{domain}') not in self.domains:
            raise exceptions.InvalidDomain(domain, self.domains)

        if True in [s.isupper() for s in username]:
            raise exceptions.InvalidUsername(username)

        self._email, self._email_hash = email, md5(email.encode('utf8')).hexdigest()

    @staticmethod
    def _make_request(uri: str) -> Union[dict, list]:
        response = requests.get(f'https://api4.temp-mail.org/request/{uri}/format/json')

        try:
            json_response = response.json()
        except JSONDecodeError:
            json_response = None

        if json_response and 'error' in json_response:
            raise exceptions.ResponseException(json_response['error'])

        response.raise_for_status()
        return json_response

    @staticmethod
    def get_domains() -> List[str]:
        return Tempmail._make_request('domains')

    def get_messages(self) -> List[dict]:
        try:
            return self._make_request(f'mail/id/{self._email_hash}')
        except exceptions.ResponseException:
            return []

    def get_message(self, message_id: str) -> dict:
        try:
            response = self._make_request(f'one_mail/id/{message_id}')
        except exceptions.ResponseException:
            raise exceptions.MessageNotFound(message_id)

        return response

    def wait_for(self, sender_contains: str = None, subject_contains: str = None,
                 text_contains: str = None, timeout: int = 120, interval: int = 5) -> dict:
        conditions = []

        if sender_contains is not None:
            conditions.append(('mail_from', sender_contains))
        if subject_contains is not None:
            conditions.append(('mail_subject', subject_contains))
        if text_contains is not None:
            conditions.append(('mail_text', text_contains))

        for _ in range(timeout // interval + 1):
            for message in self.get_messages():
                is_suitable = True

                for key, contains in conditions:
                    if contains not in message[key]:
                        is_suitable = False
                        break

                if is_suitable:
                    return message
            sleep(interval)

        raise exceptions.TimeoutException()
