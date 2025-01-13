import pytest
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from django.contrib.auth.models import User
from store.models import Collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_user_anonymous_return_401(self):
        client = APIClient()
        
        response = client.post('/store/collections/', {'title': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_admin_return_403(self):
        client = APIClient()
        client. force_authenticate(user={})
        
        response = client.post('/store/collections/', {'title': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_data_invalid_return_400(self):
        client = APIClient()
        client. force_authenticate(user=User(is_staff=True))
        
        response = client.post('/store/collections/', {'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_data_valid_return_201(self):
        client = APIClient()
        client. force_authenticate(user=User(is_staff=True))
        
        response = client.post('/store/collections/', {'title': 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

@pytest.mark.django_db
class TestGetCollection:
    def test_data_valid_return_200(self):
        client = APIClient()
        collection = baker.make(Collection)
        response = client.get(f'/store/collections/{collection.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
                    'id' : collection.id,
                    'title' : collection.title,
                }

