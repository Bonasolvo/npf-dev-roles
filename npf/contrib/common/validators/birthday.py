from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from dateutil.relativedelta import relativedelta
from datetime import datetime


@deconstructible
class BirthdayValidator(object):
    code = 'birthday'

    def __call__(self, value):
        today = datetime.today().date()

        if value > today:
            raise ValidationError('Дата рождения не может быть указана больше текущей.', code=self.code)

        if relativedelta(today, value).years > 80:
            raise ValidationError('Возраст ФЛ не должен превышать 80 лет!', code=self.code)