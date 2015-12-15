from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from npf.contrib.common.validators import DigitOnlyValidator


@deconstructible
class InsuranceCertificateValidator(DigitOnlyValidator):
    code = 'invalid'

    def __call__(self, value):
        super().__call__(value)

        if len(value) < 11:
            return

        """
        2) Контрольное число СНИЛС рассчитывается следующим образом:
        2.1) Каждая цифра СНИЛС умножается на номер своей позиции (позиции отсчитываются с конца)
        2.2) Полученные произведения суммируются
        2.3) Если сумма меньше 100, то контрольное число равно самой сумме
        2.4) Если сумма равна 100 или 101, то контрольное число равно 0
        2.5) Если сумма больше 101, то сумма делится по остатку на 101
                и контрольное число определяется остатком от деления аналогично пунктам 2.3 и 2.4
        """

        ks = value[len(value)-2:]
        k = 0
        s = 0

        while k < 9:
            k += 1
            s += (10 - k) * int(value[k-1])

        k_ost = s % 101 if s % 101 != 100 else 0

        if k_ost != int(ks):
            raise ValidationError('Контрольная суммма ССГПС не верна!')