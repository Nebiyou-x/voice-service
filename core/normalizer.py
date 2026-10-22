import re

class AmharicTextNormalizer:
    """
    Expands Ge'ez numerals, common abbreviations, agricultural metrics,
    and financial values into full phonemic Amharic text prior to TTS synthesis.
    """
    
    GEEZ_NUMERALS = {
        '፩': 'አንድ', '፪': 'ሁለት', '፫': 'ሦስት', '፬': 'አራት', '፭': 'አምስት',
        '፮': 'ስድስት', '፯': 'ሰባት', '፰': 'ስምንት', '፱': 'ዘጠኝ', '፲': 'አሥር'
    }

    ARABIC_DIGITS = {
        '0': 'ዜሮ', '1': 'አንድ', '2': 'ሁለት', '3': 'ሦስት', '4': 'አራት',
        '5': 'አምስት', '6': 'ስድስት', '7': 'ሰባት', '8': 'ስምንት', '9': 'ዘጠኝ'
    }

    ABBREVIATIONS = [
        (r'\bኪ\.ግ\b', 'ኪሎግራም'),
        (r'\bኪ/ግ\b', 'ኪሎግራም'),
        (r'\bሄ/ር\b', 'ሄክታር'),
        (r'\bብር\b', 'ብር'),
        (r'\bዶ/ር\b', 'ዶክተር'),
        (r'\bፕ/ር\b', 'ፕሮፌሰር'),
        (r'\bዓ\.ም\b', 'ዓመተ ምሕረት'),
    ]

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text:
            return ""

        # Normalize Ge'ez Punctuation
        text = text.replace('፡', ' ').replace('።', '። ')

        # Expand Abbreviations
        for pattern, replacement in cls.ABBREVIATIONS:
            text = re.sub(pattern, replacement, text)

        # Replace Ge'ez Numerals
        for gez, word in cls.GEEZ_NUMERALS.items():
            text = text.replace(gez, f" {word} ")

        # Expand standalone single Arabic digits
        for digit, word in cls.ARABIC_DIGITS.items():
            text = re.sub(rf'\b{digit}\b', word, text)

        # Clean trailing and redundant spaces
        return re.sub(r'\s+', ' ', text).strip()