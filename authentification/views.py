# Importation des modules Django nécessaires
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

# Importation des formulaires et modèles de l'application
from .forms import SignupForm, LoginForm, SearchUser, FollowUserButton
from .models import User, UserFollows


def signup_page_view(request):
    """Vue pour l'inscription d'un utilisateur."""

    # Si la requête est de type POST
    if request.method == "POST":
        # Création du formulaire d'inscription avec les données de la requête
        form = SignupForm(request.POST)

        # Si le formulaire est valide
        if form.is_valid():
            # Sauvegarde de l'utilisateur créé
            user = form.save()
            # Connexion automatique de l'utilisateur nouvellement créé
            login(request, user)
            # Redirection vers l'URL de redirection après la connexion
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        # Si la requête n'est pas de type POST, initialisation du formulaire
        form = SignupForm()

    # Affichage du formulaire d'inscription
    return render(request, "register/register_page.html", context={
        "form": form})


# Vue pour la connexion à l'interface utilisateur
def login_page_view(request):
    """Vue pour la connexion à l'interface utilisateur."""

    # Si la requête est de type POST
    if request.method == "POST":
        # Création du formulaire de connexion avec les données de la requête
        form = LoginForm(request.POST)

        # Si le formulaire est valide
        if form.is_valid():
            # Authentification de l'utilisateur
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            # Si l'authentification est réussie
            if user is not None:
                # Connexion de l'utilisateur
                login(request, user)
                # Redirection vers la page des flux
                return redirect("review:feeds_page")

            else:
                # Affichage d'un message d'erreur si l'authentification échoue
                messages.error(request, "Invalid username or password!")

    else:
        # Si la requête n'est pas de type POST, initialisation du formulaire
        form = LoginForm()
    # Affichage du formulaire de connexion
    return render(request, "login/login_page.html", context={"form": form})


# Vue pour la déconnexion de l'interface utilisateur
def logout_page_view(request):
    """Vue pour la déconnexion de l'interface utilisateur."""

    logout(request)
    return redirect("authentification:login")


# Page d'abonnement
@login_required
def abo_page_view(request, user):
    """Vue de la page d'abonnement avec la logique de suivi et de
    désabonnement, affichage des utilisateurs suivis par request.user.
    """
    # Initialisation des formulaires de recherche d'utilisateur et de suivi
    search_form = SearchUser()
    searched_user_resp = ""
    # Récupération de l'utilisateur demandé
    requested_user = User.objects.get(username=user)
    # Recherche
    searched_user_resp_btn = ''

    # Si la requête est de type POST
    if request.method == "POST":
        # Initialisation du formulaire de suivi
        flwUserBtn = FollowUserButton(request.POST)

        # Si "follow" est présente dans les données POST
        if "follow" in request.POST:
            if flwUserBtn.is_valid():
                # Récupération de l'utilisateur à suivre
                to_be_followed_user = flwUserBtn.cleaned_data[
                    "searched_to_follow"]
                try:
                    # Création d'une relation de suivi entre les utilisateurs
                    user_to_follow = User.objects.get(
                        username=to_be_followed_user)
                    # fait référence au gestionnaire d'objets (objects)
                    # associé au modèle UserFollows pour crée une nouvelle
                    # instance
                    UserFollows.objects.create(
                        user=request.user, followed_user=user_to_follow,
                    )
                except User.DoesNotExist:
                    # Affichage d'un message d'erreur si l'utilisateur
                    # n'existe pas
                    messages.error(
                        request,
                        "User does not exist. Please choose another name."
                    )

                except IntegrityError:
                    # Affichage d'un message d'erreur si la relation de suivi
                    # existe déjà
                    messages.error(request,
                                   "You are already following this User.")

            else:
                # Affichage d'un message d'erreur si le formulaire n'est pas
                # valide
                messages.error(request, "Please choose an other name.")

        # Si le formulaire contient la clé "unfollow" dans la requête POST
        elif "unfollow" in request.POST:
            # Récupérer l'ID de l'utilisateur à ne plus suivre depuis la
            # requête POST
            user_id = request.POST.get("unfollow")
            # Obtenir l'objet User correspondant à cet ID
            user_to_unfollow = User.objects.get(id=user_id)
            # Supprimer l'objet UserFollows correspondant à l'utilisateur
            # actuel et l'utilisateur à ne plus suivre
            UserFollows.objects.get(
                user=request.user, followed_user=user_to_unfollow
            ).delete()

        # Sinon, si la clé "search" est présente dans la requête POST
        elif "search" in request.POST:
            # Créer une instance du formulaire de recherche avec les données
            # de la requête POST
            search_form = SearchUser(request.POST)
            # Si le formulaire de recherche est valide
            if search_form.is_valid():
                # Récupération du terme de recherche à partir des données
                # netoyées du formulaire
                query = search_form.cleaned_data['search']
                # Recherche d'un utilisateur dont le nom d'utilisateur
                # contient le terme de recherche (insensible à la casse)
                searched_user = User.objects.filter(
                    username__icontains=query).first()
                # Si un utilisateur correspondant est trouvé
                if searched_user:
                    # Stocker l'utilisateur recherché dans une variable de
                    # réponse
                    searched_user_resp = searched_user
                    # Créer une instance du bouton de suivi avec le nom
                    # d'utilisateur de l'utilisateur recherché comme valeur
                    # initiale
                    searched_user_resp_btn = FollowUserButton(initial={
                        'searched_to_follow': searched_user.username})

                else:
                    messages.error(
                        request,
                        "User does not exist. Please choose another name."
                    )

    # Récupérer tous les utilisateurs suivis par l'utilisateur actuel
    followed_users = request.user.following.all()
    # Récupérer tous les utilisateurs qui suivent l'utilisateur actuel
    followed_by_others = UserFollows.objects.filter(followed_user=request.user)

    # Filtrage des utilisateurs disponibles pour le suivi (éviter de se suivre
    # soi-même ou les superutilisateurs)
    users = (
        # Exclusion des superutilisateurs
        User.objects.filter(is_superuser=False)
        # Exclusion des utilisateurs déjà suivis par l'utilisateur actuel
        .exclude(id__in=request.user.following.values_list(
                "followed_user_id", flat=True)  # renvoie une liste plate
                # (une seule liste d'IDs) plutôt qu'une liste de tuples.
        )
        .exclude(id=request.user.id)
    )

    # Construction du contexte contenant les users pour le rendu de la page
    context = {
        "users": users,
        'search_form': search_form,
        'searched_user_resp': searched_user_resp,
        'searched_user_btn': searched_user_resp_btn,
        'requested_user': requested_user,
        "followed_users": followed_users,
        "followed_by_others": followed_by_others,
    }

    # Rendu de la page d'abonnement
    return render(request, "abo/abo_page.html", context)
