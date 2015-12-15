from django.core import validators


class MaxLengthValidator(validators.MaxLengthValidator):
    clean = lambda self, x: len(str(x))
