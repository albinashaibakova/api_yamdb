from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.validators import validator_for_username
from api_yamdb.settings import (
    INVALID_CHAR,
    USERNAME_FIELD_MAX_LENGTH,
)
from reviews.models import (Category,
                            Comment,
                            Genre,
                            Review,
                            Title)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        return validator_for_username(value)


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_FIELD_MAX_LENGTH,
        validators=[validator_for_username],
        required=True
    )
    email = serializers.EmailField(
        required=True,
        max_length=USERNAME_FIELD_MAX_LENGTH
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(email=email,
                               username=username).exists():
            return data
        elif (User.objects.filter(email=email).exists()
              and User.objects.filter(username=username).exists()):
            raise serializers.ValidationError(
                {'email': 'Email already registered',
                 'username': 'Username already taken'})
        elif User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Email already registered'}
            )
        elif User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': 'Username already taken'}
            )
        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        user, created = User.objects.get_or_create(
            email=email,
            username=username
        )
        return user


class UserGetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_FIELD_MAX_LENGTH,
        required=True,
        validators=[validator_for_username]
    )
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
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'category', 'genre', 'rating')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         many=True,
                                         allow_empty=False,
                                         allow_null=False,
                                         queryset=Genre.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'category', 'genre',)

    def to_representation(self, instance):
        return TitleListSerializer(instance).data


class AuthorSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )


class ReviewSerializer(AuthorSerializer):
    class Meta:
        model = Review
        fields = ('id', 'text', 'author',
                  'score', 'pub_date')
        read_only_fields = ('author', 'pub_date', 'title',)

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
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('author', 'pub_date', 'review',)
