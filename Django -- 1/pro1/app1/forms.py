from django.forms import forms
from captcha.fields import CaptchaField


class CP(forms.Form):
    c = CaptchaField()
