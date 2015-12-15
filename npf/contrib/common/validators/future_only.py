from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils import timezone


@deconstructible
class FutureOnlyValidator(object):

    code = 'future_only'

    def __call__(self, value):

        now = timezone.now()

        if value < now:
            raise ValidationError('Дата и время не могут быть указаны меньше текущих.',
                                  code=self.code)
