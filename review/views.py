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


# feeds page
@login_required
def feeds_page_view(request):
    """the general feeds page with all reviews of users which I follow,
    my reviews and reviews of user how are following me
    displays all tickets, without any review, of users I am following
    """

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

    # sort Reviews and Tickets by time_created
    posts = sorted(
        chain(reviews, tickets), key=lambda post: post.time_created,
        reverse=True
    )

    return render(request, "feeds/feeds_page.html", context={"posts": posts})


@login_required
def ask_review_view(request):
    """button 'Ask for a review' on feeds and posts page
    - create a new Ticket which can be reviewed"""

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            form.save()

            return redirect("review:feeds_page")

    else:
        form = TicketForm()

    return render(request, "feeds/ask_review_page.html", context={
        "form": form})


@login_required
def create_review_view(request):
    """button 'Create a review' on feeds and posts page
    - creates a Review which includes a new Ticket"""

    if request.method == "POST":
        ask_review_form = TicketForm(request.POST, request.FILES)
        create_review_form = ReviewForm(request.POST)

        if ask_review_form.is_valid() and create_review_form.is_valid():
            ask_review = ask_review_form.save(commit=False)
            create_review = create_review_form.save(commit=False)

            ask_review.user = request.user

            create_review.ticket = ask_review
            create_review.user = request.user

            ask_review_form.save()
            create_review_form.save()

            return redirect("review:feeds_page")

    else:
        ask_review_form = TicketForm()
        create_review_form = ReviewForm()

    context = {
        "ask_review_form": ask_review_form,
        "create_review_form": create_review_form,
    }

    return render(request, "feeds/create_review_page.html", context)


@login_required
def create_review_for_ticket_view(request, pk):
    """button 'Create a review' for a Ticket on feeds page
    - display the Ticket and creates a Review for this chosen Ticket"""

    get_ticket = Ticket.objects.get(pk=pk)

    if request.method == "POST":
        create_review_ticket_form = ReviewForm(request.POST)

        if create_review_ticket_form.is_valid():
            create_review = create_review_ticket_form.save(commit=False)

            create_review.ticket = get_ticket
            create_review.user = request.user

            create_review_ticket_form.save()

            return redirect("review:feeds_page")

    else:
        create_review_ticket_form = ReviewForm()

    context = {
        "get_ticket": get_ticket,
        "create_review_ticket_form": create_review_ticket_form,
    }

    return render(request, "feeds/create_review_ticket_page.html", context)


@login_required
def posts_page_view(request):
    """displays all created tickets/reviews of request.user"""

    reviews = Review.objects.filter(user=request.user)
    tickets = Ticket.objects.filter(user=request.user)

    context = {
        "reviews": reviews,
        "tickets": tickets,
    }

    return render(request, "posts/posts_page.html", context)


@login_required
def posts_modify_review_view(request, pk):
    """the 'Modify' button on post page for a Review
    - modify of Review possible with attached Ticket
    - if request.user is the creator of the Review and Ticket,
        then Review and Ticket can be modified
    """

    # receive the review data from database:
    instance_review = get_object_or_404(Review, pk=pk)

    # check if the author of the review is the same creator of the ticket:
    if (
        request.user == instance_review.ticket.user
        and request.user == instance_review.user
    ):
        # receive ticket data from review:
        instance_ticket = instance_review.ticket

        if request.method == "POST":
            review_form = ReviewForm(request.POST, instance=instance_review)
            ticket_form = TicketForm(
                request.POST, request.FILES, instance=instance_ticket
            )

            if review_form.is_valid() and ticket_form.is_valid():
                review_form.save()
                ticket_form.save()

                messages.success(request,
                                 "Your post was modified with success!")

                return redirect("review:posts_page")

        else:
            review_form = ReviewForm(instance=instance_review)
            ticket_form = TicketForm(instance=instance_ticket)

        context = {
            "review_form": review_form,
            "ticket_form": ticket_form,
        }

        return render(request, "posts/posts_review_modify_page.html", context)

    # author of review and creator of ticket are not the same:
    else:
        if request.method == "POST":
            review_form = ReviewForm(request.POST, instance=instance_review)

            if review_form.is_valid():
                review_form.save()

                messages.success(request,
                                 "Your post was modified successfully!")

                return redirect("review:posts_page")

        else:
            review_form = ReviewForm(instance=instance_review)

    context = {
        "review_form": review_form,
        "instance_review": instance_review,
    }

    return render(request, "posts/posts_review_modify_page.html", context)


def posts_modify_ticket_view(request, pk):
    """the button 'Modify' on posts page for a Ticket
    - modify a ticket on posts page"""

    instance_ticket = get_object_or_404(Ticket, pk=pk)

    if request.user == instance_ticket.user:
        if request.method == "POST":
            ticket_form = TicketForm(
                request.POST, request.FILES, instance=instance_ticket
            )

            if ticket_form.is_valid():
                ticket_form.save()

                messages.success(request,
                                 "Your ticket was modified with success!")

                return redirect("review:posts_page")

        else:
            ticket_form = TicketForm(instance=instance_ticket)

    context = {"ticket_form": ticket_form}

    return render(request, "posts/posts_ticket_modify_page.html", context)


@login_required
def posts_delete_view(request, pk):
    """this view will delete the chosen item: a Ticket or a Review with
    attached Ticket
    """

    ticket = get_object_or_404(Ticket, id=pk)

    if request.user == ticket.user:
        ticket.delete()

        messages.success(request, "This post is successfully deleted.")

        return redirect("review:posts_page")

    return render(request, "posts/posts_page.html")
