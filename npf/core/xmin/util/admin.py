from django.contrib import admin
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.http import Http404
from django.utils.html import escape
from django.contrib.contenttypes.models import ContentType

from npf.core.printform.models import Template


try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


def get_admin_for_model(model):
    return get_model_and_admin(model._meta.app_label, model._meta.model_name)


def get_model_and_admin(app_label, model_name):
    """
    Возвращает модель и админскую модель по названию django приложения и имени модели.
    """
    for (model, model_admin) in admin.site._registry.items():
        if model._meta.app_label == app_label and model._meta.model_name == model_name:
            return model, model_admin
    return None


def get_model_and_admin_or_404(app_label, module_name):
    """
    Возвращает модель и админскую модель по названию django приложения и имени модели.
    Если модели не найдены, возвращает ошибку 404
    """
    model_and_admin = get_model_and_admin(app_label, module_name)
    if model_and_admin is None:
        raise Http404
    return model_and_admin


def get_admin_urls_for_model(request, model):
    """
    Возвращает ссылки для добавления и изменения объектов для указанной модели
    при условии наличия соответствующих прав у пользователя.
    """
    admin_urls = {}

    model_and_admin = get_admin_for_model(model)
    if model_and_admin is None:
        return admin_urls

    model_admin = model_and_admin[1]

    app_label = model._meta.app_label
    has_module_perms = request.user.has_module_perms(app_label)

    """
    Проверка прав
    """
    if has_module_perms:
        perms = model_admin.get_model_perms(request)

        info = (app_label, model._meta.model_name)
        if perms.get('change', False):
            try:
                admin_urls['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=admin.site.name)
            except NoReverseMatch:
                pass
        if perms.get('add', False):
            try:
                admin_urls['add_url'] = reverse('admin:%s_%s_add' % info, current_app=admin.site.name)
            except NoReverseMatch:
                pass

    return admin_urls


def flatten_choices(choices):
    # Normalize to strings.
    output = []
    for option_value, option_label in choices:
        if isinstance(option_label, (list, tuple)):
            output.append({'id': '', 'type': 'header', 'description': escape(force_unicode(option_value))})
            for option in option_label:
                output.append({'id': option[0], 'type': 'item', 'description': escape(force_unicode(option[1]))})
        else:
            output.append({'id': option_value, 'type': 'header_item',
                           'description': escape(force_unicode(option_label))})
    return output


def get_app_list(request):
    def _actions_exists(model_admin, model):
        if bool(model_admin.get_action_choices(request)):
            return True
        ct = ContentType.objects.get_for_model(model, not model._meta.proxy)
        if Template.objects.filter(model=ct).exists():
            return True
        return False

    app_dict = {}
    user = request.user
    for model, model_admin in admin.site._registry.items():
        """
        Для каждой модели и админской модели в системе формируем набор мета данных:
         - набор полей с их мета данными
         - человеко-понятные названия и имена классов
         - права доступа
         - и т.п.
        Данные используются при первоначальной загрузке и инициалиции приложения
        """
        app_label = model._meta.app_label
        app_name = model._meta.app_config.verbose_name
        has_module_perms = user.has_module_perms(app_label)

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                fields = []

                for field in model._meta.fields:
                    field_config = {
                        'name': field.name,
                        'verbose_name': field.verbose_name,
                        'app': app_label,
                        'model': model._meta.model_name,
                        'field_class': "%s.%s" % (field.__class__.__module__, field.__class__.__name__),
                        'default': field.get_default(),
                        'editable': field.editable,
                        'allow_blank': field.blank,
                        'help_text': field.help_text,
                        'max_length': field.max_length,
                        'choices': flatten_choices(field.choices)
                    }

                    if isinstance(field, models.ForeignKey):
                        field_config['related'] = {'class': "%s.%s" % (field.rel.to.__module__, field.rel.to.__name__)}
                        field_config['related'].update(get_admin_urls_for_model(request, field.rel.to))

                    fields.append(field_config)

                model_dict = {
                    'app': app_label,
                    'model': model._meta.model_name,
                    'model_name': model._meta.object_name,
                    'verbose_name': model._meta.verbose_name,
                    'verbose_name_plural': model._meta.verbose_name_plural,
                    'perms': perms,
                    'list_display': model_admin.get_list_display(request),
                    'list_editable': model_admin.list_editable,
                    'list_per_page': model_admin.list_per_page,
                    'search_fields': model_admin.get_search_fields(request),
                    'fields': fields,
                    'actions': _actions_exists(model_admin, model)
                }

                model_dict.update(get_admin_urls_for_model(request, model))

                if hasattr(model_admin, 'columns'):
                    model_dict['columns'] = model_admin.get_columns(request)
                else:
                    model_dict['columns'] = []

                if 'is_tree' in dir(model_admin):
                    model_dict.update({'is_tree': True})

                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    app_dict[app_label] = {
                        'app': app_label,
                        'name': app_name,
                        'app_url': reverse('admin:app_list', kwargs={'app_label': app_label},
                                           current_app=admin.site.name),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

    # Sort the apps alphabetically.
    app_list = list(app_dict.values())
    app_list.sort(key=lambda x: x['name'])

    return app_list


def get_actions(request, model, model_admin):
    actions = model_admin.get_action_choices(request)
    template_actions = []
    ct = ContentType.objects.get_for_model(model, not model._meta.proxy)
    templates = Template.objects.filter(model=ct)
    for template in templates:
        template_actions.append({
            'text': template.name,
            'name': 'create_doc_' + template.name
        })
    if template_actions:
        actions.append(('create_doc', 'Сделать документ', template_actions))
    return actions
