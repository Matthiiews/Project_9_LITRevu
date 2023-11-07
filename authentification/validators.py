from django.core.exceptions import ValidationError


class ContainsLetterValidator:
    """
    Validateur de mot de passe personnalisé pour s'assurer que le mot de passe
    contient au moins une lettre.
    """
    def validate(self, password, user=None):
        """
        Valider si le mot de passe contient au moins une lettre.

        Args:
            password (str): Le mot de passe à valider.
            user: Paramètre non utilisé, requis pour la signature du
            validateur personnalisé.

        Raises:
            ValidationError: Si le mot de passe ne contient aucune lettre.
        """
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                'The password must contain at least one letter',
                code='password_no_letters'
            )

    def get_help_text(self):
        """
        Obtenir le texte d'aide à afficher à l'utilisateur.

        Returns:
            str: Message de texte d'aide.
        """
        return
    'Your password must contain at least one upper or lower case letter.'
