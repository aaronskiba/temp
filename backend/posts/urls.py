from django.urls import path

from .views import PostDetail, PostList, CommentList, LikedList, PostLikeList, CommentLikeList

urlpatterns = [
    # posts
    path("authors/<id>/posts/", PostList.as_view(), name="post_list"),
    path("authors/<author_id>/posts/<post_id>", PostDetail.as_view(), name="post_detail"),
    # comments
    path("authors/<author_id>/posts/<post_id>/comments", CommentList.as_view(), name="comment_list"),
    # likes
    path("authors/<author_id>/liked/", LikedList.as_view(), name="liked_list"),
    path("authors/<author_id>/posts/<post_id>/likes", PostLikeList.as_view(), name="post_like_list"),
    path("authors/<author_id>/posts/<post_id>/comments/<comment_id>/likes", CommentLikeList.as_view(), name="comment_like_list"),
]