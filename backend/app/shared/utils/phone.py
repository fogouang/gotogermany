"""
app/shared/utils/phone.py
Normalisation des numéros au format international (E.164), seul format utilisable par WhatsApp.
"""
import re

DEFAULT_COUNTRY_CODE = "237"  # Cameroun


def normalize_phone(raw: str | None) -> str | None:
    """
    "6 90 00 00 00"    -> "+237690000000"
    "237690000000"     -> "+237690000000"
    "00237690000000"   -> "+237690000000"
    "+49 151 2345678"  -> "+491512345678"
    Vide -> None. Lève ValueError si le numéro est inexploitable.
    """
    if raw is None or not raw.strip():
        return None

    value = raw.strip()
    has_plus = value.startswith("+")
    digits = re.sub(r"\D", "", value)

    if not has_plus and digits.startswith("00"):
        digits, has_plus = digits[2:], True

    if not has_plus:
        # Numéro camerounais local : 9 chiffres commençant par 6 (mobile) ou 2 (fixe)
        if len(digits) == 9 and digits[0] in "62":
            digits = DEFAULT_COUNTRY_CODE + digits
        elif not (digits.startswith(DEFAULT_COUNTRY_CODE) and len(digits) == 12):
            raise ValueError("Numéro de téléphone invalide.")

    # E.164 : 8 à 15 chiffres, indicatif inclus
    if not 8 <= len(digits) <= 15:
        raise ValueError("Numéro de téléphone invalide.")

    return f"+{digits}"