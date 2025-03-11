import string
import random



def generate_string(n: int):
    letters_digits = string.ascii_letters + string.digits
    result = ""
    for i in range(n):
        result += random.choice(letters_digits)

    return result