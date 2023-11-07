from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from .forms import SignupForm, LoginForm, SearchUser, FollowUserButton
from .models import User, UserFollows


def signup_page_view(request):
    """register view"""

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupForm()

    return render(request, "register/register_page.html", context={
        "form": form})


def login_page_view(request):
    """login to user interface"""

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            if user is not None:
                login(request, user)
                return redirect("review:feeds_page")

            else:
                messages.error(request, "Invalid username or password!")

    else:
        form = LoginForm()

    return render(request, "login/login_page.html", context={"form": form})


def logout_page_view(request):
    """logout from user interface"""

    logout(request)
    return redirect("authentification:login")


# Page d'abonnement
@login_required
def abo_page_view(request, user):
    """abo page, with follow and unfollow logic, see which users is following
    request.user"""
    search_form = SearchUser()
    searched_user_resp = ""
    requested_user = User.objects.get(username=user)
    # search
    searched_user_resp_btn = ''

    if request.method == "POST":

        flwUserBtn = FollowUserButton(request.POST)

        if "follow" in request.POST:
            if flwUserBtn.is_valid():
                to_be_followed_user = flwUserBtn.cleaned_data[
                    "searched_to_follow"]
                try:
                    user_to_follow = User.objects.get(
                        username=to_be_followed_user)
                    UserFollows.objects.create(
                        user=request.user, followed_user=user_to_follow,
                    )
                except User.DoesNotExist:
                    messages.error(
                        request,
                        "User does not exist. Please choose another name."
                    )

                except IntegrityError:
                    messages.error(request,
                                   "You are already following this User.")

            else:
                messages.error(request, "Please choose an other name.")

        elif "unfollow" in request.POST:
            user_id = request.POST.get("unfollow")
            user_to_unfollow = User.objects.get(id=user_id)
            UserFollows.objects.get(
                user=request.user, followed_user=user_to_unfollow
            ).delete()

        elif "search" in request.POST:
            search_form = SearchUser(request.POST)
            if search_form.is_valid():
                query = search_form.cleaned_data['search']
                searched_user = User.objects.filter(
                    username__icontains=query).first()
                if searched_user:
                    searched_user_resp = searched_user
                    searched_user_resp_btn = FollowUserButton(initial={
                        'searched_to_follow': searched_user.username})

                else:
                    messages.error(
                        request,
                        "User does not exist. Please choose another name."
                    )

    followed_users = request.user.following.all()
    followed_by_others = UserFollows.objects.filter(followed_user=request.user)

    users = (
        User.objects.filter(is_superuser=False)
        .exclude(id__in=request.user.following.values_list(
                "followed_user_id", flat=True)
        )
        .exclude(id=request.user.id)
    )

    context = {
        "users": users,
        'search_form': search_form,
        'searched_user_resp': searched_user_resp,
        'searched_user_btn': searched_user_resp_btn,
        'requested_user': requested_user,
        "followed_users": followed_users,
        "followed_by_others": followed_by_others,
    }

    return render(request, "abo/abo_page.html", context)
