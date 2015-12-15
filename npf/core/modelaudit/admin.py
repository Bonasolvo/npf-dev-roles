from django.contrib import admin

from .models import AuditFieldsMixin


class AuditFieldsAdminMixin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if isinstance(obj, AuditFieldsMixin):
            if not change:
                obj.added_by_user = request.user
                obj.modified_by_user = request.user
            else:
                obj.modified_by_user = request.user

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if not issubclass(formset.model, AuditFieldsMixin):
            super().save_formset(request, form, formset, change)
            return

        formset.save(commit=False)

        for obj in formset.new_objects:
            obj.added_by_user = request.user
            obj.modified_by_user = request.user
            obj.save()

        for obj, fields in formset.changed_objects:
            obj.modified_by_user = request.user
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()