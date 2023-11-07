from django.urls import path

from .views import (
    feeds_page_view,
    ask_review_view,
    create_review_view,
    create_review_for_ticket_view,
    posts_page_view,
    posts_modify_review_view,
    posts_delete_view,
    posts_modify_ticket_view,
)

app_name = "review"

urlpatterns = [
    path("feeds/", feeds_page_view, name="feeds_page"),
    path("ask_review/", ask_review_view, name="ask_review"),
    path("create_review/", create_review_view, name="create_review"),
    path(
        "create_review_ticket/<int:pk>/",
        create_review_for_ticket_view,
        name="create_review_ticket",
    ),
    path("posts/", posts_page_view, name="posts_page"),
    path(
        "posts/review/modify/<int:pk>/",
        posts_modify_review_view,
        name="posts_modify_review_page",
    ),
    path(
        "posts/ticket/modify/<int:pk>/",
        posts_modify_ticket_view,
        name="posts_modify_ticket_page",
    ),
    path("posts/delete/<int:pk>/", posts_delete_view,
         name="posts_delete_page"),
]
