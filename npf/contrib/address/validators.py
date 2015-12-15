from django.core.cache import cache
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from fias.models import SocrBase

import re


@deconstructible
class AddressValidator(RegexValidator):
    code = 'invalid_address'
    cyrillic_only_message = _('Допускаются символы только на кирилице')
    wrong_socr_message = _('На {0}-ой позиции допускаются следующие сокращения: {1}')
    default_message = _('Не корректный формат адреса, используйте сокращения для уточнения адресных объектов, уровни '
                        'ардресных объектов отделяйте запятыми, например: г Москва, пл Красная')

    def __call__(self, value):
        self.regex = re.compile(r"^[а-яА-ЯёЁ\s,\-]+$", re.IGNORECASE)
        self.message = self.cyrillic_only_message

        super().__call__(value)

        parts = value.split(',')
        level = 1

        # Список возможных адресных сокращений для каждого уровня адреса (обл.|г.|р-н...)
        socr_lvl_map = {1: [1],
                        2: [2, 3, 4, 7],
                        3: [3, 4, 7, 91],
                        4: [4, 5, 7, 91],
                        5: [5, 6, 7, 8, 90, 91]}

        socr = cache.get('fias_socr_terms', {})

        if not socr:
            for term in SocrBase.objects.all().order_by('level', 'item_weight'):
                if term.level not in socr:
                    socr[term.level] = [term.scname]
                else:
                    socr[term.level].append(term.scname)

            cache.set('fias_socr_terms', socr)

        # Проверка каждого уровня введенного адреса на соответствие массиву возможных сокращений
        for part in parts:
            if ' ' in part:
                try:
                    term, obj_term = part.strip().split(' ', 1)
                    term = term.rstrip('.')
                except ValueError:
                    raise ValidationError(self.default_message, code=self.code)

                socr_valid = False
                allowed_socr = ''

                for lvl in socr_lvl_map[level]:
                    if term in socr[lvl]:
                        socr_valid = True
                        break

                    if allowed_socr:
                        allowed_socr += ', '

                    allowed_socr += ', '.join(socr[lvl])

                if not socr_valid:
                    raise ValidationError(self.wrong_socr_message.format(level, allowed_socr), code=self.code)

            else:
                raise ValidationError(self.default_message, code=self.code)

            level += 1