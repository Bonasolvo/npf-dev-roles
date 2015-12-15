from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
import re


@deconstructible
class DigitOnlyValidator(RegexValidator):
    regex = re.compile(r'^\d+$')
    message = 'Допускаются только цифры от 0 до 9.'