from typing import List


def generate_token(issuer: str, groups: List[str], ticket_id: int):
    return "-".join([str(issuer)] + groups + [str(ticket_id)])
