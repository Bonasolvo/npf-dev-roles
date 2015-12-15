from fias.models import SocrBase


class Socr(SocrBase):

    class Meta:
        verbose_name = 'Сокращениие наименования адресного объекта'
        verbose_name_plural = 'Список сокращений'
        proxy = True