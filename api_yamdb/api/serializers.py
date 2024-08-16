from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Title, Review

User = get_user_model()

USERNAME_FIELD_MAX_LENGTH = 150


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserGetTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_FIELD_MAX_LENGTH,
        required=True)
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'category', 'genre', 'rating')

    def get_rating(self, obj):
        # todo
        return None


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all())

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'category', 'genre',)


class AuthorSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )


class ReviewSerializer(AuthorSerializer):

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title',)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        if Review.objects.filter(
            author=self.context['request'].user,
            title=get_object_or_404(
                Title,
                id=self.context['view'].kwargs.get('title_id'))
        ).exists():
            raise serializers.ValidationError(
                'Можно добавить только один '
                'отзыв на произведение'
            )
        return data


class CommentSerializer(AuthorSerializer):

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review',)
