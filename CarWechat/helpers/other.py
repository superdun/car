import random
import string
def getRandomStr(len):
    return  ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(len))