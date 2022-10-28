from django.db import models
from django.utils import timezone
from utils.model_utils import generate_random_string
from authors.models import Author
from django.utils.translation import gettext_lazy as _


class ContentType(models.TextChoices):
    # for HTML you will want to strip tags before displaying
    TEXT_MARKDOWN = "text/markdown", _("markdown") # common mark
    TEXT_PLAIN = "text/plain", _("text/plain") # UTF-8
    APPLICATION = "application/base64", _("application")
    PNG = "image/png;base64", _("png") # this is an embedded png -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
    JPEG = "image/jpeg;base64", ("jpeg") # this is an embedded jpeg


class Post(models.Model):

    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC', _("Public")
        FRIENDS = 'FRIENDS', _("Friends")
        PRIVATE = 'PRIVATE', _("Private")

    type = models.CharField(max_length=4, default="post", editable=False)
    title = models.CharField(max_length=255, null=False)
    id = models.CharField(primary_key=True, editable=False, max_length=255, default=generate_random_string)
    source = models.URLField()
    origin = models.URLField()
    description = models.CharField(max_length=255)
    contentType = models.CharField(choices=ContentType.choices, null=False, max_length=255,default=ContentType.TEXT_PLAIN)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    published = models.DateTimeField(default=timezone.now, blank=False)
    visibilty = models.CharField(choices=Visibility.choices, max_length=7,default=Visibility.PUBLIC)
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    
class Category(models.Model):

    category = models.CharField(max_length=255) # TODO: Do we know what all of the potential categories are?
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('category', 'post'))

        
class Comment(models.Model):

    type = models.CharField(max_length=7, default="comment", editable=False)
    # the author that commented
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="comments")
    # the Post that was commented on
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    contentType = models.CharField(choices=ContentType.choices, null=False, max_length=255, default=ContentType.TEXT_PLAIN)
    content = models.TextField()
    published = models.DateTimeField(default=timezone.now, blank=False)

    

class PostLike(models.Model):

    type = models.CharField(max_length=4, default="like", editable=False)
    # the author that clicked 'like'
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="post_likes")
    # the Post that was liked
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    
class CommentLike(models.Model):

    type = models.CharField(max_length=4, default="like", editable=False)
    # the author that clicked 'like'
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="comment_likes")
    # the Comment that was liked
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")