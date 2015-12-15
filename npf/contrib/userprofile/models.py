"""
NPF userprofile models module
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    UserManager, Group
from django.core.mail import send_mail
from django.db import models
from django.core import validators
from django.utils import timezone


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """
    Extended default user model

    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(
        _('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. '
                    'This value may contain only letters, numbers '
                    'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    email = models.EmailField(_('email address'), blank=True)
    role = models.ForeignKey('role.Role', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class ProxyGroup(Group):
    """
    Django group proxy model
    """
    class Meta:
        proxy = True
        app_label = "role"
        verbose_name = 'Группа'
        verbose_name_plural = 'Группа'


class ProxyUser(UserProfile):
    """
    User profile proxy model
    """
    class Meta:
        proxy = True
        app_label = "role"
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'
