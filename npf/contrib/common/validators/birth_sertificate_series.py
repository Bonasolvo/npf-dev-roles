from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
import re


@deconstructible
class BirthCertificateSeriesValidator(RegexValidator):
    regex = re.compile(r'^[IVXLCDM]{2}[А-ЯёЁ]{2}$|^[IVXLCDM]{2}\-[А-ЯёЁ]{2}$|^[IVXLCDM]{2}\s[А-ЯёЁ]{2}$')
    message = 'Укажите корректную серию свидетельства о рождении.'