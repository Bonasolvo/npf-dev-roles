import sys
import codecs

from django.core.management.commands.dumpdata import Command as Dumpdata
from django.utils import six


class Command(Dumpdata):
    def execute(self, *args, **options):
        if six.PY3:
            options['stdout'] = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        else:
            options['stdout'] = codecs.getwriter('utf-8')(sys.stdout, 'strict')
        return super(Command, self).execute(*args, **options)