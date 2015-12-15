from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MiddleNameValidator(object):
    ending = ['вич', 'вна']
    code = 'middle_name'

    def __call__(self, value):
        if value[-3:] not in self.ending or len(value) <= 3:
            raise ValidationError('Отчество должно оканчиваться на "вич" или "вна"', code=self.code)