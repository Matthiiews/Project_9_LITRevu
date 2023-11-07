from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    """Formulaire d'inscription."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")


class LoginForm(forms.Form):
    """Formulaire de connexion pour l'interface utilisateur."""

    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)


class AboForm(forms.Form):
    """Formulaire pour la page d'abonnement, permettant de suivre et de ne
    plus suivre les utilisateurs.
    """

    search = forms.CharField(max_length=50, label=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_search(self):
        search = self.cleaned_data["search"]

        # Impossible de se suivre soi même :
        if self.user and self.user.username == search:
            # Remplacé par des messages dans le vue
            raise forms.ValidationError("You can not follow yourself!")

        # Impossible de suivre un admin/superutilisateur :
        if User.objects.filter(username=search, is_superuser=True).exists():
            # Remplacé par des messages dans la vue
            raise forms.ValidationError(
                "Please choose an other name to follow!")

        return search


class FollowUserButton(forms.Form):
    searched_to_follow = forms.CharField(widget=forms.HiddenInput())


class SearchUser(forms.Form):
    search = forms.CharField(
        label=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Rechercher un utilisateur'
            }
        )
    )
    search_user_id = forms.BooleanField(widget=forms.HiddenInput, initial=True)
