from flask import request, redirect, url_for
from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms.fields import TextField, PasswordField, HiddenField

from urlparse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc and \
           test_url.path != url_for('user.login')

def get_redirect_target():
    for target in request.values.get('next'), request.referrer, request.url:
        if not target:
            continue
        if is_safe_url(target):
            return target

class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super(RedirectForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='frontend.index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))

class LoginForm(RedirectForm):
    username = TextField('Username', validators=[])
    password = PasswordField('Password', validators=[])
    next = HiddenField('next', validators=[])