from random import choices
from string import ascii_lowercase, ascii_uppercase, digits


def id_gen(length=6):
    pool = ascii_lowercase + ascii_uppercase + digits
    generated_id = "".join(choices(pool, k=length))
    return generated_id


if __name__ == '__main__':
    print(id_gen(6))
