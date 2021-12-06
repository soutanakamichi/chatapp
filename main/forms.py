from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # AuthenticationForm を追加
from .models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email",)

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # html の表示を変更可能にします
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["password"].widget.attrs["class"] = "form-control"

class TalkForm(forms.Form):
    talk = forms.CharField(label="talk")

# 以下を追加
class UserNameSettingForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)
        labels = {"username": "新しいユーザー名"}

# 以下を追加
class MailSettingForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "新しいメールアドレス"