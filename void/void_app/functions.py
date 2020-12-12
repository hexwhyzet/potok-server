import time
from random import choices
from string import ascii_lowercase, ascii_uppercase, digits

# from .models import Link

from base64 import urlsafe_b64encode, urlsafe_b64decode


def id_gen(length=6):
    pool = ascii_lowercase + ascii_uppercase + digits
    generated_id = "".join(choices(pool, k=length))
    return generated_id


# def link_token_gen():
#     if Link.objects.count() == 0:
#         return 'a'
#     else:
#         last_token = Link.objects.last().token
#         new_token = next_token(last_token)
#         return new_token


def next_token(token):
    base = 52

    def to_number(c):
        if 'a' <= c <= 'z':
            return ord(c) - ord('a')
        else:
            return ord(c) - ord('A') + 26

    def to_char(n):
        if n < 26:
            return chr(ord('a') + n)
        else:
            return chr(ord('A') + n - 26)

    def next_num(v):
        for i in range(len(v)):
            if v[i] != base - 1:
                v[i] += 1
                break
            else:
                v[i] = 0
                if i == len(v) - 1:
                    v.append(0)

    conv_token = list(map(to_number, reversed(token)))
    next_num(conv_token)
    new_token = ''.join(reversed(list(map(to_char, conv_token))))
    return new_token


def token_from_id(int_id):
    bytes_id = int_id.to_bytes((int_id.bit_length() + 7) // 8, 'big') or b'\0'
    token = urlsafe_b64encode(bytes_id).removesuffix(b'=').removesuffix(b'=').decode("ascii")
    return token


def id_from_token(token):
    if len(token) % 4 != 0:
        token += '=' * (4 - len(token) % 4)
    bytes_token = urlsafe_b64decode(token)
    int_id = int.from_bytes(bytes_token, 'big')
    return int_id


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
