from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from posts.models import Group, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    Представления для работы с постами.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """
        Создает новый пост с указанием автора.
        """
        return serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для работы с группами (только для чтения).
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.AllowAny,)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Представления для работы с комментариями.
    """

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_post_object(self):
        """
        Получает объект поста на основе переданного id поста в URL.
        """
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def get_queryset(self):
        """
        Получает комментарии для указанного поста.
        """
        post = self.get_post_object()
        return post.comments.all()

    def perform_create(self, serializer):
        """
        Создает новый комментарий для указанного поста.
        """
        post = self.get_post_object()
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet,
):
    """
    Представления для работы с подписками.
    """

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('following', )
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        """
        Возвращает все подписки пользователя, сделавшего запрос.
        """
        return self.request.user.followers.all()

    def perform_create(self, serializer):
        """
        Подписать пользователя, сделавшего запрос на пользователя,
        переданного в теле запроса.
        """
        serializer.save(user=self.request.user)
