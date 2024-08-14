from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Genre, Title

User = get_user_model()


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


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
