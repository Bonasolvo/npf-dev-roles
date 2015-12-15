from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
import re


@deconstructible
class CyrillicOnlyValidator(RegexValidator):
    regex = re.compile(r'^[а-яА-ЯёЁ\s]+$', re.IGNORECASE)
    message = 'Допускаются символы только на кирилице'