from django.contrib.auth import authenticate, login  # 追加
from django.shortcuts import redirect, render  # redirectを追加
from .forms import SignUpForm  # 追加
from django.db.models import Q # 追加
from django.shortcuts import get_object_or_404 # 追加
from .forms import (
    SignUpForm,
    LoginForm,
    TalkForm, # 追加
    UserNameSettingForm, # 追加
    MailSettingForm, # 追加
)
from django.contrib.auth.decorators import login_required  # 追加
from .models import Talk # Talk を追加
from .models import User  # 追加
from django.contrib.auth.forms import PasswordChangeForm # 追加
from django.contrib.auth.mixins import LoginRequiredMixin # 追加
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView # LogoutViewを追加
from django.urls import reverse_lazy # 追加

def index(request):
    return render(request, "main/index.html")


def signup_view(request):
    return render(request, "main/signup.html")


# login_view 関数を消して以下を追加
class Login(LoginView):
    """ログインページ

    GET の時は authentication_form で指定された form を template_name で指定したテンプレートに表示する。
    POST の時は login を試みる。→成功すれば setting の LOGIN_REDIRECT_URL で指定された URL に飛ぶ
    """
    authentication_form = LoginForm
    template_name = "main/login.html"


def signup_view(request):

    if request.method == "GET":
        form = SignUpForm()

    elif request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            #モデルフォームは form の値を models にそのまま格納できる save() メソッドがあるので便利
            form.save()
            # フォームから username を読み取る
            username = form.cleaned_data.get("username")
            # フォームから"password1"を読み取る
            password = form.cleaned_data.get("password1")
            # 認証情報のセットを検証するには authenticate() を利用してください。
            # このメソッドは認証情報をキーワード引数として受け取ります。
            user = authenticate(username=username, password=password)
            # 検証する対象はデフォルトでは username と password であり、
            # その組み合わせを個々の認証バックエンドに対して問い合わせ、認証バックエンドで認証情報が有効とされれば User オブジェクトを返します。# もしいずれの認証バックエンドでも認証情報が有効と判定されなければ PermissionDenied エラーが送出され、None が返されます。
            # つまり、autenticateメソッドは"username"と"password"を受け取り、その組み合わせが存在すればその User を返し、不正であれば None を返します。
            if user is not None:
                # あるユーザーをログインさせる場合は、login() を利用してください。
                # この関数は HttpRequest オブジェクトと User オブジェクトを受け取ります。
                # ここでの User は認証バックエンド属性を持ってる必要があり、authenticate() が返す User は user.backend（認証バックエンド属性）を持つので連携可能。
                login(request, user)
            return redirect("/")
    context = {"form": form}
    return render(request, "main/signup.html", context)

# 以下を追加
@login_required
def friends(request):
    user = request.user
    # 自分以外のユーザーのオブジェクトを、最新のトークの送信日時が新しい順に取得
    friends = User.objects.exclude(id=user.id)
    context = {
        "friends": friends,
    }
    return render(request, "main/friends.html", context)

# 既存talk_room関数を消して以下を追加
@login_required
def talk_room(request, user_id):
    user = request.user
    # get_object_or_404 は、第一引数にモデル名、その後任意の数のキーワードを受け取り、もし合致するデータが存在するならそのデータを、存在しないなら 404 エラーを発生させます
    friend = get_object_or_404(User, id=user_id)
    # 自分が送信者で上の friend が受信者であるデータ、または friend が送信者で friend が受信者であるデータをすべて取得します
    talk = Talk.objects.filter(Q(talk_from=user, talk_to=friend) | Q(talk_to=user, talk_from=friend))
    # 送信日時が古い順に並べ直します
    talk = talk.order_by("time")

    form = TalkForm()
    context = {
        "form": form,
        "talk": talk,
    }

    # メッセージ送信時の処理
    if request.method == "POST":
        # 送信内容を取得
        form = TalkForm(request.POST)
        if form.is_valid():
            # 送信内容からメッセージを取得
            text = form.cleaned_data.get("talk")
            # 送信者、受信者、メッセージを与えて保存
            new_talk = Talk(talk=text, talk_from=user, talk_to=friend)
            new_talk.save()
            return redirect("talk_room", user_id)

    return render(request, "main/talk_room.html", context)


@login_required
def setting(request):
    return render(request, "main/settings.html")

# 以下を追加
@login_required
def username_change(request):
    user = request.user
    if request.method == "GET":
        # instance を指定することで、指定したインスタンスのデータにアクセスできます
        form = UserNameSettingForm(instance=user)

    elif request.method == "POST":
        form = UserNameSettingForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # 保存後、完了ページに遷移します
            return redirect("username_change_done")

    context = {
        "form":form,
    }
    return render(request, "main/username_change.html", context)


@login_required
def username_change_done(request):
    return render(request, "main/username_change_done.html")


# 以下を追加
@login_required
def mail_change(request):
    user = request.user
    if request.method == "GET":
        form = MailSettingForm(instance=user)

    elif request.method == "POST":
        form = MailSettingForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("mail_change_done")

    context = {
        "form":form,
    }
    return render(request,"main/mail_change.html", context)


@login_required
def mail_change_done(request):
    return render(request, "main/mail_change_done.html")

# 以下を追加
class PasswordChange(PasswordChangeView):
    """Django 組み込みパスワード変更ビュー

    template_name : 表示するテンプレート
    success_url : 処理が成功した時のリダイレクト先
    form_class : パスワード変更フォーム
    """

    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "main/password_change.html"


class PasswordChangeDone(PasswordChangeDoneView):
    """Django 標準パスワード変更後ビュー"""
    template_name = "main/password_change_done.html"

# 以下を追加
class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    pass