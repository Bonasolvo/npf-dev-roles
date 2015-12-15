from django.test import TestCase

from npf.core.counter.api import Api
from npf.core.counter.models import NamedCounter


class CounterTestCase(TestCase):
    def setUp(self):
        NamedCounter.objects.create(name="counter_95")
        NamedCounter.objects.create(name="counter_96", value=3)
        NamedCounter.objects.create(name="counter_97", value=5)
        NamedCounter.objects.create(name="counter_98", value=88)

    def test_parse_counter(self):
        names = Api('1012-{counter_95}/95').parse_mask()
        self.assertEqual(names[0], 'counter_95')

    def test_generate_one_counter(self):
        api = Api('1012-{counter_95}/95')
        names = Api('1012-{counter_95}/95').parse_mask()
        new_counter_first = api.generate(names)

        new_counter_second = Api('1012-{counter_95}/95').generate()

        self.assertEqual(new_counter_first, '1012-00001/95')
        self.assertEqual(new_counter_second, '1012-00002/95')

    def test_generate_many_counter(self):
        new_counter = Api('1012-{counter_95}{counter_96}{counter_97}{counter_98}/95{counter_98}').generate()

        self.assertEqual(new_counter, '1012-00001000040000600089/9500089')