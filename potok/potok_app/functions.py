from random import choices
from string import ascii_lowercase, ascii_uppercase, digits

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

ALPHABET = ascii_uppercase + ascii_lowercase + digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'


def id_gen(length=6):
    pool = ascii_lowercase + ascii_uppercase + digits
    generated_id = "".join(choices(pool, k=length))
    return generated_id


def token_from_id(n):
    if n < 0:
        return SIGN_CHARACTER + token_from_id(-n)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0:
            break
    return ''.join(reversed(s))


def id_from_token(s):
    if s[0] == SIGN_CHARACTER:
        return -id_from_token(s[1:])
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n


def extension_from_url(url):
    return url.split(".")[-1].split("?")[0]


def is_valid_url(url):
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        return False
    return True


if __name__ == '__main__':
    pass
    # token = 'a'
    # for i in range(20000000, 1000000000):
    #     id = i
    #     token = token_from_id(i)
    #     re_id = id_from_token(token)
    #     # print(token)
    #     if id != re_id:
    #         print("Look", id)
