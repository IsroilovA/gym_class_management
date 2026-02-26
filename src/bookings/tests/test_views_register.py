import pytest
from django.urls import reverse
from django.contrib.auth.models import User

pytestmark = pytest.mark.integration

def test_register_get(client):
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200
    assert 'registration/register.html' in [t.name for t in response.templates]

def test_register_post_valid(client, db):
    url = reverse('register')
    data = {
        'username': 'newuser123',
        'email': 'newuser123@example.com',
        'password1': 'strongpass123',
        'password2': 'strongpass123',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('login')
    
    assert User.objects.filter(username='newuser123').exists()

def test_register_post_invalid_passwords_mismatch(client, db):
    url = reverse('register')
    data = {
        'username': 'newuser123',
        'email': 'newuser123@example.com',
        'password1': 'strongpass123',
        'password2': 'differentpass',
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser123').exists()
    assert 'form' in response.context
    assert response.context['form'].errors
