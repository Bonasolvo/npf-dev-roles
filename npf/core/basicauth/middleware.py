from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.template import loader, Context
from django.http import HttpResponse
from django.contrib.auth.signals import user_logged_out
import base64


IS_LOGGED_OUT_USER = '_auth_user_is_logged_out'


class BasicAuthMiddleware(AuthenticationMiddleware):
    """
    Базовая аутентификация (всплывающая форма для ввода логина/пароля при входе в приложение)
    """
    def __init__(self):
        self._is_user_logged_out = False
        user_logged_out.connect(self.user_logged_out)

    def user_logged_out(self, request, user, **kwargs):
        self._is_user_logged_out = True

    def unauthorized(self):
        c = Context()
        t = loader.get_template('unauthorized.html')
        response = HttpResponse(content=t.render(c), content_type='text/html; charset=UTF-8')
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        return response

    def process_request(self, request):
        super().process_request(request)

        self._is_user_logged_out = False

        if request.user.is_authenticated():
            return None

        if not 'HTTP_AUTHORIZATION' in request.META:
            return self.unauthorized()

        if IS_LOGGED_OUT_USER in request.session:
            return self.unauthorized()

        authentication = request.META['HTTP_AUTHORIZATION']
        auth_method, auth = authentication.split(' ', 1)

        if 'basic' != auth_method.lower():
            return self.unauthorized()

        auth = base64.b64decode(auth.strip())

        try:
            auth = auth.decode('utf-8')
        except UnicodeDecodeError:
            auth = auth.decode('windows-1251')

        username, password = auth.split(':', 1)

        form = AuthenticationForm(data={'username': username, 'password': password})
        if not form.is_valid():
            return self.unauthorized()

        login(request, form.get_user())

    def process_response(self, request, response):
        if IS_LOGGED_OUT_USER in request.session:
            del request.session[IS_LOGGED_OUT_USER]

        if self._is_user_logged_out:
            self._is_user_logged_out = False
            request.session[IS_LOGGED_OUT_USER] = True
            response = self.unauthorized()
            del response['WWW-Authenticate']

        return response