from django import forms

from .models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "description", "image")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("headline", "rating", "body")

    rating = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={
            "class": "inline"
        }),
        choices=[
            (0, " -0 "),
            (1, " -1 "),
            (2, " -2 "),
            (3, " -3 "),
            (4, " -4 "),
            (5, " -5 "),
        ],
    )
