"""
NPF roles models module
"""
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Role(models.Model):
    """
    Role model
    """
    role_name = models.CharField(max_length=255)
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), blank=True,
        help_text=_('The groups this role belongs to. A user will '
                    'get all permissions granted to each of '
                    'their groups.'),
        related_name="role_set", related_query_name="role")
    permissions = models.ManyToManyField(
        Permission, verbose_name=_('role permissions'), blank=True,
        help_text=_('Specific permissions for this role.'),
        related_name="role_set", related_query_name="role")

    class Meta:
        """
        Role model meta options
        """
        verbose_name = "Роль"
        verbose_name_plural = "Роль"

    def __str__(self):
        """
        Model representation string
        """
        return self.role_name
