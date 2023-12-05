from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Classe représentant un utilisateur personnalisé héritant
    de la classe AbstractUser.
    """

    pass


class UserFollows(models.Model):
    """Modèle pour gérer les relations de suivi entre utilisateurs."""

    # Définition des métadonnées du modèle
    class Meta:
        verbose_name = "UserFollow"
        verbose_name_plural = "UserFollows"
        unique_together = ["user", "followed_user"]

    # Utilisateur qui effectue le suivi
    user = models.ForeignKey(
        "authentification.User",
        on_delete=models.CASCADE,
        related_name="following",  # Utilisé pour accéder aux relations de
        # suivi depuis un utilisateur
        verbose_name=_("user"),
    )

    # Utilisateur suivi
    followed_user = models.ForeignKey(
        "authentification.User",
        on_delete=models.CASCADE,
        related_name="followed_by",  # Utilisé pour accéder aux relations de
        # suivi pour un utilisateur suivi
        verbose_name=_("follower"),
    )

    # Méthode spéciale pour afficher une représentation textuelle de l'objet
    def __str__(self):
        return f"{self.user} - is following: {self.followed_user}"
