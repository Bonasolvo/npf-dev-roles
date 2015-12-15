from django.db import models
from fias.models import AddrObj, SocrBase


class AddressQuerySet(models.QuerySet):
    """
    Набор данные для прокси модели адресов
    """
    def by_term(self, term, exact=False):
        """
        Фильтрация по введенной пользователем части адреса
        """
        filter_params = None

        level = 0
        result_parts = []
        result = []
        parts = term.split(',')

        parts_len = len(parts)

        """
        Проверяем иерархию для всех объектов перед последней запятой
        """
        if parts_len > 1:

            for part in parts[:-1]:
                socr_term, obj_term = part.strip().split(' ', 1)
                socr_term = socr_term.rstrip('.')
                part_qs = self.filter(shortname__iexact=socr_term, formalname__iexact=obj_term)

                if level > 0:
                    part_qs = part_qs.filter(parentguid=result_parts[level-1].aoguid)

                if len(part_qs) == 1:
                    level += 1
                    result_parts.append(part_qs[0])
                elif len(part_qs) > 1:
                    raise Exception('Lots of options???')
                else:
                    return None

        """
        Строку после последней запятой проверяем более тщательно
        """

        last = parts[-1].lstrip()
        last_len = len(last)

        # Это сокращение и начало названия объекта?
        if ' ' in last:
            socr_term, obj_term = last.split(' ', 1)
            socr_term = socr_term.rstrip('.')

            if exact:
                search = dict(scname__iexact=socr_term)
            else:
                search = dict(scname__icontains=socr_term)

            sqs = SocrBase.objects.filter(**search).distinct()

            if level > 0:
                sqs = sqs.filter(level__gt=result_parts[-1].aolevel)

            sqs_len = len(sqs)
            obj_term = obj_term.strip()

            if sqs_len > 1:
                levels = []
                socrs = []
                for s in sqs:
                    levels.append(s.level)
                    socrs.append(s.scname)

                filter_params = dict(
                    aolevel__in=set(levels),
                    shortname__in=set(socrs),
                )
            elif sqs_len == 1:
                filter_params = dict(
                    aolevel=sqs[0].level,
                    shortname=sqs[0].scname,
                )

            if filter_params:
                if obj_term:
                    if exact:
                        search = dict(formalname__iexact=obj_term)
                    else:
                        search = dict(formalname__icontains=obj_term)

                    filter_params.update(**search)

                if level > 0:
                    filter_params.update(parentguid=result_parts[-1].aoguid, aolevel__gt=result_parts[-1].aolevel)

        # Это только сокращение?
        elif last_len < 10:
            if exact:
                search = {'scname__iexact': last}
            else:
                search = {'scname__icontains': last}

            sqs = SocrBase.objects.filter(**search)

            if level > 0:
                sqs = sqs.filter(level__gt=result_parts[-1].aolevel)

            sqs_len = len(sqs)
            if sqs_len:
                result = ((None, s.scname) for s in sqs)
            else:
                if exact:
                    filter_params = dict(formalname__iexact=last)
                else:
                    filter_params = dict(formalname__icontains=last)

                if level > 0:
                    filter_params.update(parentguid=result_parts[-1].aoguid, aolevel__gt=result_parts[-1].aolevel)

        prefix = ', '.join((r.get_formal_name() for r in result_parts)) if result_parts else ''

        if result:
            if prefix:
                # return NO_ERR_RESP, False, ((k, '{0}, {1}'.format(prefix, v)) for k, v in result)
                return prefix, result

            # return NO_ERR_RESP, False, result
            return None, result

        if filter_params is not None:
            result = self.order_by('aolevel').filter(**filter_params)[:10]

            if prefix:
                return prefix, result

            else:
                return None, result


class AddressManager(models.Manager):

    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)

    def by_term(self, term, exact=False):
        return self.get_queryset().by_term(term, exact)


class Address(AddrObj):
    """
    Прокси модель адресов ФИАС с фильтрацией по введенной части адреса
    """
    class Meta:
        proxy = True

    objects = AddressManager()