from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import CharField, Q, Value
from django.shortcuts import render, redirect, get_object_or_404
from itertools import chain

from .forms import (
    TicketForm,
    ReviewForm,
)
from .models import Ticket, Review


#  Vue de la page générale des flux
@login_required
def feeds_page_view(request):
    """"La page générale des flux affiche toutes les critiques des
    utilisateurs que je suis, mes propres critiques ainsi que les critiques
    des utilisateurs qui me suivent. Elle affiche également tous les billets
    sans aucune critique, des utilisateurs que je suis en train de suivre.
    """

    # Récupération des critiques et des billets associés à l'utilisateur
    # connecté
    reviews = (
        Review.objects.filter(
            Q(user__followed_by__user=request.user)
            | Q(user=request.user)
            | Q(ticket__user=request.user)
        )
        .distinct()
        .annotate(type_of_content=Value("REVIEW", CharField()))
    )
    tickets = (
        Ticket.objects.filter(reviews__isnull=True)
        .filter(Q(user__followed_by__user=request.user) | Q(user=request.user))
        .distinct()
        .annotate(type_of_content=Value("TICKET", CharField()))
    )

    # Fusionner et trier les critiques et les billets par date de création
    posts = sorted(
        chain(reviews, tickets), key=lambda post: post.time_created,
        reverse=True
    )

    # Rendre la page avec la liste des critiques et des billets
    return render(request, "feeds/feeds_page.html", context={"posts": posts})


# Vue pour demander une critique
@login_required
def ask_review_view(request):
    """"Le bouton 'Demander une critique' sur la page des flux et
    des publications
    - crée un nouveau ticket pouvant être examiné.
    """

    if request.method == "POST":
        # Création d'un formulaire de ticket avec les données de la requête
        form = TicketForm(request.POST, request.FILES)

        # Si le formulaire est valide
        if form.is_valid():
            # Création d'une instance de ticket liée à l'utilisateur connecté
            ticket = form.save(commit=False)
            ticket.user = request.user
            form.save()

            # Redirection vers la page des flux
            return redirect("review:feeds_page")

    else:
        # Si la requête n'est pas de type POST, initialisation du formulaire
        # de ticket
        form = TicketForm()

    # Rendre la page avec le formulaire de ticket
    return render(request, "feeds/ask_review_page.html", context={
        "form": form})


# Vue pour créer une critique
@login_required
def create_review_view(request):
    """"Bouton 'Créer une critique' sur la page des flux et des publications
    - crée une critique qui inclut un nouveau ticket.
    """

    if request.method == "POST":
        # Création des formulaires de ticket et de critique avec les données
        # de la requête
        ask_review_form = TicketForm(request.POST, request.FILES)
        create_review_form = ReviewForm(request.POST)

        # Si les formulaires sont valides
        if ask_review_form.is_valid() and create_review_form.is_valid():
            # Création d'une instance de ticket liée à l'utilisateur connecté
            ask_review = ask_review_form.save(commit=False)
            ask_review.user = request.user

            # Création d'une instance de critique liée au ticket et à
            # l'utilisateur connecté
            create_review = create_review_form.save(commit=False)
            create_review.ticket = ask_review
            create_review.user = request.user

            # Sauvegarde des instances
            ask_review_form.save()
            create_review_form.save()

            # Redirection vers la page des flux
            return redirect("review:feeds_page")

    else:
        # Si la requête n'est pas de type POST, initialisation des formulaires
        ask_review_form = TicketForm()
        create_review_form = ReviewForm()

    # Rendre la page avec les formulaires de ticket et de critique
    context = {
        "ask_review_form": ask_review_form,
        "create_review_form": create_review_form,
    }

    return render(request, "feeds/create_review_page.html", context)


# Vue pour créer une critique pour un ticket
@login_required
def create_review_for_ticket_view(request, pk):
    """Bouton 'Create a review' pour un ticket sur la page des flux
    - affiche le ticket et crée une critique pour ce ticket choisi
    """

    # Récupération du ticket choisi
    get_ticket = Ticket.objects.get(pk=pk)

    if request.method == "POST":
        # Création d'un formulaire de critique avec les données de la requête
        create_review_ticket_form = ReviewForm(request.POST)

        # Si le formulaire de critique est valide
        if create_review_ticket_form.is_valid():
            # Création d'une instance de critique liée au ticket et à
            # l'utilisateur connecté
            create_review = create_review_ticket_form.save(commit=False)

            create_review.ticket = get_ticket
            create_review.user = request.user

            # Sauvegarde de l'instance de critique
            create_review_ticket_form.save()

            # Redirection vers la page des flux
            return redirect("review:feeds_page")

    else:
        # Si la requête n'est pas de type POST, initialisation du formulaire
        # de critique
        create_review_ticket_form = ReviewForm()

    # Rendre la page avec le ticket et le formulaire de critique
    context = {
        "get_ticket": get_ticket,
        "create_review_ticket_form": create_review_ticket_form,
    }

    # Rendre la page des flux de la création de billets
    return render(request, "feeds/create_review_ticket_page.html", context)


# Vue pour afficher tous les billets/critiques créés par l'utilisateur connecté
@login_required
def posts_page_view(request):
    """Affiche tous les billets/critiques créés par l'utilisateur connecté"""

    # Récupération des critiques et des billets liés à l'utilisateur connecté
    reviews = Review.objects.filter(user=request.user)
    tickets = Ticket.objects.filter(user=request.user)

    # Contexte pour rendre la page
    context = {
        "reviews": reviews,
        "tickets": tickets,
    }

    # Rendre la page avec les critiques et les billets
    return render(request, "posts/posts_page.html", context)


# Vue pour modifier une critique
@login_required
def posts_modify_review_view(request, pk):
    """Le bouton 'Modifier' sur la page des publications pour une critique
    - modification possible de la critique avec le ticket associé
    - si request.user est le créateur de la critique et du ticket,
        alors la critique et le ticket peuvent être modifiés
    """

    # Récupération des données de la critique à partir de la base de données:
    instance_review = get_object_or_404(Review, pk=pk)

    # Vérification si l'auteur de la critique est également le créateur du
    # ticket:
    if (
        request.user == instance_review.ticket.user
        and request.user == instance_review.user
    ):
        # Récupération des données du ticket lié à la critique:
        instance_ticket = instance_review.ticket

        if request.method == "POST":
            # Création des formulaires de critique et de ticket avec les
            # données de la requête
            review_form = ReviewForm(request.POST, instance=instance_review)
            ticket_form = TicketForm(
                request.POST, request.FILES, instance=instance_ticket
            )

            # Si les formulaires sont valides
            if review_form.is_valid() and ticket_form.is_valid():
                # Sauvegarde des modifications de la critique et du ticket
                review_form.save()
                ticket_form.save()

                # Affichage d'un message de succès
                messages.success(request,
                                 "Your post was modified with success!")

                # Redirection vers la page des publications
                return redirect("review:posts_page")

        else:
            # Si la requête n'est pas de type POST, initialisation des
            # formulaires
            review_form = ReviewForm(instance=instance_review)
            ticket_form = TicketForm(instance=instance_ticket)

        # Contexte pour rendre la page de modification
        context = {
            "review_form": review_form,
            "ticket_form": ticket_form,
        }

        # Rendre la page de modification de la critique et du ticket
        return render(request, "posts/posts_review_modify_page.html", context)

    # Si l'auteur de la critique et le créateur du ticket ne sont pas les mêmes
    else:
        if request.method == "POST":
            # Création du formulaire de critique avec les données de la requête
            review_form = ReviewForm(request.POST, instance=instance_review)

            # Si le formulaire de critique est valide
            if review_form.is_valid():
                # Sauvegarde des modifications de la critique
                review_form.save()

                # Affichage d'un message de succès
                messages.success(request,
                                 "Your post was modified successfully!")

                # Redirection vers la page des publications
                return redirect("review:posts_page")

        else:
            # Si la requête n'est pas de type POST, initialisation du
            # formulaire de critique
            review_form = ReviewForm(instance=instance_review)

    # Contexte pour rendre la page de modification de la critique
    context = {
        "review_form": review_form,
        "instance_review": instance_review,
    }

    # Retour à la page de modification de la critique
    return render(request, "posts/posts_review_modify_page.html", context)


def posts_modify_ticket_view(request, pk):
    """Le bouton 'Modifier' sur la page des publications pour un billet
    - modifier un billet sur la page des publications
    """

    # Récupération des données du billet à partir de la base de données
    instance_ticket = get_object_or_404(Ticket, pk=pk)

    # Vérification si l'utilisateur connecté est le créateur du billet
    if request.user == instance_ticket.user:
        if request.method == "POST":
            # Création du formulaire de billet avec les données de la requête
            ticket_form = TicketForm(
                request.POST, request.FILES, instance=instance_ticket
            )

            # Si le formulaire de billet est valide
            if ticket_form.is_valid():
                # Sauvegarde des modifications du billet
                ticket_form.save()

                # Affichage d'un message de succès
                messages.success(request,
                                 "Your ticket was modified with success!")

                # Redirection vers la page des publications
                return redirect("review:posts_page")

        else:
            # Si la requête n'est pas de type POST, initialisation du
            # formulaire de billet
            ticket_form = TicketForm(instance=instance_ticket)
    # Contexte pour rendre la page de modification du billet
    context = {"ticket_form": ticket_form}
    # Rendre la page de modification du billet
    return render(request, "posts/posts_ticket_modify_page.html", context)


@login_required
def posts_delete_view(request, pk):
    """Cette vue supprimera l'élément choisi : un billet ou une critique avec
    le billet associé
    """

    ticket = get_object_or_404(Ticket, id=pk)

    if request.user == ticket.user:
        ticket.delete()

        # Affichage d'un message de succès
        messages.success(request, "This post is successfully deleted.")
        # Redirection vers la page des publications
        return redirect("review:posts_page")

    return render(request, "posts/posts_page.html")
