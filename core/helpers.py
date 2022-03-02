def letterToFrenchWord(letter:str, number:int=1):
    dic = {
        "s": "seconde",
        "S": "seconde",
        "m": "minute",
        "h": "heure",
        "H": "heure",
        "j": "jour",
        "d": "jour",
        "J": "jour",
        "D": "jour",
        "M": "mois",
        "a": "an",
        "A": "an",
        "y": "an",
        "Y": "an"
    }

    if letter not in dic: return None
    result = dic[letter]
    if number > 1: result += "s"
    
    return result
