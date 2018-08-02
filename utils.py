import math

def WordOfText(s):
    s = s.strip().lower()
    #regex <[^>]*>.*<\/[^>]*> -> '' , replace html to empty
    # s = s.replace(',', ' ')
    s = s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
    s = ' '.join(s.split())
    return s.split(' ')

def formatText(s):
    s = s.strip().lower()
    s = s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
    return s


def separate(sentence):
    import re
    # return re.split("\.|,", sentence)
    return re.split("\.", sentence)


def cosine_similarity(v1, v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i];
        y = v2[i]
        sumxx += x * x
        sumyy += y * y
        sumxy += x * y
    return sumxy / math.sqrt(sumxx * sumyy)