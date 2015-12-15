"""
NPF userprofile admin module
"""
from django.contrib import admin
from django.contrib.auth.models import Group

from npf.core.xmin.admin import XminAdmin, UserExtAdmin
from npf.contrib.userprofile.models import ProxyUser, ProxyGroup


class UserProfileAdmin(UserExtAdmin):
    """
    Userprofile admin class
    """
    fieldsets = (
        ("Логин", {
            "fields": (
                "username",
                "password"
            )
        }),
        ("Персональная информация", {
            "fields": (
                "first_name",
                "last_name",
                "email"
            ),
        }),
        ("Права доступа", {
            "fields": (
                "is_active",
                "is_superuser",
                "role",
                "groups",
                "user_permissions"
            )
        }),
        ("Важные даты", {
            "fields": (
                "date_joined",
                "last_login"
            )
        }),
    )

admin.site.unregister(Group)
admin.site.register(ProxyUser, UserProfileAdmin)
admin.site.register(ProxyGroup, XminAdmin)

