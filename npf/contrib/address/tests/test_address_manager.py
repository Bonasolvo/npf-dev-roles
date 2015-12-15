from unittest import TestCase
from django.utils.encoding import force_text
from npf.contrib.address.models import Address


class TestAddressManager(TestCase):

    def test_address_by_term(self):
        prefix, result = Address.objects.by_term('г Москва, п Московский', exact=True)

        self.assertTrue(len(result) == 1)
        self.assertEqual('г Москва, п Московский', force_text(result[0]))

        prefix, result = Address.objects.by_term('г Москва, п Московский', exact=False)

        self.assertTrue(len(result) == 2)
        self.assertEqual(['г Москва, п Московский', 'г Москва, пр-кт Московский'],
                         list(['{0}, {1}'.format(prefix, x) for x in result]))