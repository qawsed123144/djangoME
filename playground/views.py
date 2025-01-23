from django.views.decorators.cache import cache_page
from django.http import JsonResponse, HttpResponse
import requests
import logging

def homepage(request):
    data = {
        "title": "My Homepage",
        "description": "Welcome to my Django-powered homepage!"
    }
    return JsonResponse(data) 

logger = logging.getLogger(__name__)

@cache_page(60)
def cache_test(request):
    try:
        logger.info('Calling httpbin')
        response = requests.get('https://httpbin.org/delay/2')
        logger.info('httpbin called')
        data = response.json()
        return JsonResponse(data=data)
    except request.ConnectionError as e:
        logger.critical(e)
    return JsonResponse(data=data)

