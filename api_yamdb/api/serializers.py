from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Genre, Title

User = get_user_model()

USERNAME_FIELD_MAX_LENGTH = 150
EMAIL_FIELD_MAX_LENGTH = 254
FIRST_NAME_FIELD_MAX_LENGTH = 150
LAST_NAME_FIELD_MAX_LENGTH = 150


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_FIELD_MAX_LENGTH,
        required=True)
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_MAX_LENGTH,
        required=True)
    first_name = serializers.CharField(
        max_length=FIRST_NAME_FIELD_MAX_LENGTH,
        required=False
    )
    last_name = serializers.CharField(
        max_length=LAST_NAME_FIELD_MAX_LENGTH,
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_FIELD_MAX_LENGTH,
        required=True)
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_MAX_LENGTH,
        required=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if username == 'me':
            raise serializers.ValidationError(
                'Cannot use username me'
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Username is already taken'
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Email is already registered'
            )
        return data

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
        fields = ('id', 'name', 'year', 'description', 'category', 'genre', 'rating')

    def get_rating(self, obj):
        #todo
        return None


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug', many=True, queryset=Genre.objects.all())

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'category', 'genre',)
