from random import choices
from string import ascii_lowercase, ascii_uppercase, digits

from .models import Link


def id_gen(length=6):
    pool = ascii_lowercase + ascii_uppercase + digits
    generated_id = "".join(choices(pool, k=length))
    return generated_id


def link_token_gen():
    if Link.objects.count() == 0:
        return 'a'
    else:
        last_token = Link.objects.last().token
        new_token = next_token(last_token)
        return new_token


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


if __name__ == '__main__':
    token = 'a'
    for i in range(int(1e6)):
        print(token)
        token = link_token_gen(token)
