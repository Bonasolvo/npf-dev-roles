import re

from django.core.exceptions import ValidationError
from django.db import transaction

from npf.core.counter.models import NamedCounter


class Api():
    _mask = ''

    def __init__(self, mask):
        self._mask = mask

    def parse_mask(self):
        if not self._mask or self._mask == '':
            raise ValidationError('Invalid mask')

        p = re.compile("\{([^\{]+)\}")
        matches_counter = p.findall(self._mask)
        if matches_counter is None:
            raise ValidationError('Invalid mask')

        names = matches_counter

        return names

    def generate(self, names=None):
        if names is None:
            names = self.parse_mask()

        with transaction.atomic():
            counters = NamedCounter.objects.select_for_update().filter(name__in=names)
            # Обновляем найденные счетчикик
            for counter in counters:
                counter.value += 1
                counter.save()

            # Создаем новые счетчики
            if counters.count() < len(names):
                counter_names = counters.values_list('name', flat=True).order_by('name')
                for name in names:
                    if name not in counter_names:
                        NamedCounter.objects.create(name=name)

        counters = NamedCounter.objects.filter(name__in=names)

        if len(counters) == 0:
            raise ValidationError('Not found counters with that mask.')

        # Генерируем маску с новыми счетчиками
        counter_mask = self._mask
        for counter in counters:
            counter_mask = counter_mask.replace('{' + counter.name + '}', '%0*d' % (5, counter.value))

        return counter_mask