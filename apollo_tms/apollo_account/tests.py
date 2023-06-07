from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from apollo_account.models import ApolloUser
import apollo_account.views as view 

class UserOperations(TestCase):
    '''
        Test operations on the user view
    '''
    def setUp(self):
        self.client = APIClient()
        self.user = ApolloUser.objects.create_user(
            username="jacob", email="jacob@jack.com", password="top_secret"
        )

    def test_create(self):
        '''
            Test the registration step, given by drf authorization but who knows
        '''
        self.client.post('/registration/',
                                    {
                                        "username": "john",
                                        "email": "john@lennon.com",
                                        "password1": "yokoonoismylife",
                                        "password2": "yokoonoismylife"
                                    }, format = 'json')
        
        response = self.client.login(username="john", password="yokoonoismylife")
        
        self.assertEqual(response, True)
        