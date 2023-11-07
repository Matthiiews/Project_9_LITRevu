from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image


class Ticket(models.Model):
    """A ticket is related to a Review."""

    title = models.CharField(max_length=128, verbose_name=_("title of ticket"))
    description = models.TextField(
        max_length=2048, verbose_name=_(
            "description of ticket"), blank=True, null=True
    )
    user = models.ForeignKey(
        "authentification.User",
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name=_("creator of ticket"),
    )
    image = models.ImageField(
        upload_to="images", verbose_name=_("image"), blank=True, null=True
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("ticket created at")
    )

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            img.thumbnail((250, 375))
            img.save(self.image.path)


class Review(models.Model):
    """A Review has a rating and a ticket."""

    ticket = models.ForeignKey(
        "review.Ticket",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("ticket"),
    )
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("rating"),
    )
    headline = models.CharField(max_length=128, verbose_name=_(
        "title of review"))
    body = models.TextField(verbose_name=_("comment"), blank=True, null=True)
    user = models.ForeignKey(
        "authentification.User",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("author of review"),
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("review created at")
    )

    def __str__(self):
        return f"{self.headline}, {self.ticket}"
