import random
import string

def generate_short_url(length=6):
    """
    주어진 길이의 랜덤 단축 URL을 생성합니다.

    이 함수는 알파벳 대문자, 소문자, 숫자를 포함한 문자열에서 지정된 길이만큼
    랜덤하게 선택하여 단축 URL을 생성합니다. 기본적으로 6자리 길이의 단축 URL을
    생성하지만, `length` 매개변수를 통해 다른 길이의 단축 URL을 생성할 수 있습니다.

    Args:
        length (int): 생성할 단축 URL의 길이입니다. 기본값은 6입니다.

    Returns:
        str: 생성된 랜덤 단축 URL입니다.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
