from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from pyshop.permission import IsAdminOrReadOnly
from datetime import datetime
from rest_framework import status

from .serializers import ArticleSerializer
from .es import search_article, add_article, get_article_by_id



class ArticleESView(GenericAPIView):
    serializer_class = ArticleSerializer
    queryset = []

    def get(self, request):
        query = request.GET.get("q", "")
        data = search_article(query)
        return Response(data)

    def post(self, request):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
        serializer = ArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        res = add_article(data["title"], data["content_json"])
        return Response(res)
    


class ArticleDetailView(APIView):
    def get(self, request, id):
        article = get_article_by_id(id)
        if not article:
            return Response({'error': '找不到文章'}, status=status.HTTP_404_NOT_FOUND)
        return Response(article)
