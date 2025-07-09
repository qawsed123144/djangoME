from rest_framework import serializers
from .models import Article, ArticleAttachment


class ArticleSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField(required=False)
    content_json = serializers.JSONField()
