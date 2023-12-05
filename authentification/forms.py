from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


# Formulaire d'inscription héritant de UserCreationForm de Django
class SignupForm(UserCreationForm):
    """Formulaire d'inscription."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")


# Formulaire de connexion pour l'interface utilisateur
class LoginForm(forms.Form):
    """Formulaire de connexion pour l'interface utilisateur."""

    # Champs pour le nom d'utilisateur et le mot de passe
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)


# Formulaire pour la page d'abonnement, permettant de suivre et de ne plus
# suivre les utilisateurs
class AboForm(forms.Form):
    """Formulaire pour la page d'abonnement, permettant de suivre et de ne
    plus suivre les utilisateurs.
    """

    # Champ de recherche pour entrer le nom d'utilisateur
    search = forms.CharField(max_length=50, label=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    # Validation personnalisée pour le champ de recherche
    def clean_search(self):
        search = self.cleaned_data["search"]

        # Impossible de se suivre soi même :
        if self.user and self.user.username == search:
            # Lancement d'une exception en cas d'erreur
            raise forms.ValidationError("You can not follow yourself!")

        # Impossible de suivre un admin/superutilisateur :
        if User.objects.filter(username=search, is_superuser=True).exists():
            # exception remplacé par des messages dans la vue
            raise forms.ValidationError(
                "Please choose an other name to follow!")

        return search


# Formulaire pour le bouton de suivi d'utilisateur
class FollowUserButton(forms.Form):
    # Champ caché pour stocker l'utilisateur à suivre
    searched_to_follow = forms.CharField(widget=forms.HiddenInput())


# Formulaire de recherche d'utilisateur
class SearchUser(forms.Form):
    # Champ de recherche avec un widget de placeholder
    search = forms.CharField(
        label=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Rechercher un utilisateur'
            }
        )
    )
    # Champ caché indiquant s'il faut inclure l'ID de l'utilisateur dans les
    # résultats
    search_user_id = forms.BooleanField(widget=forms.HiddenInput, initial=True)
