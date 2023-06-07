from django.test import  TestCase
from rest_framework.test import APIClient

from apollo_account.models import ApolloUser

class UserOperations(TestCase):
    '''
        Test operations on the user view
    '''
    def setUp(self):
        self.client = APIClient()
        self.admin = ApolloUser.objects.create_superuser(username='admin', password='supersecret')

    def test_operations(self):
        '''
            Test the registration, login, put, patch methods, given by drf authorization and viewset code but who knows
        '''
        self.client.post('/registration/',
                                    {
                                        "username": "john",
                                        "email": "john@lennon.com",
                                        "password1": "yokoonoismylife",
                                        "password2": "yokoonoismylife"
                                    }, format = 'json')
        
        response = self.client.post('/api/v1/login/', 
                                    {
                                        "username":"john", 
                                        "password":"yokoonoismylife"
                                    }, format = 'json')
        # expect a 200 response
        self.assertEqual(response.status_code, 200)

        # partially update the user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['key'])
        response = self.client.patch('/api/v1/user/',
                                    {
                                        "first_name": "carl",
                                    }, format = 'json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "carl")

        # update the user
        response = self.client.put('/api/v1/user/',
                                    {
                                        "username": "henry",
                                        "first_name": "frank",
                                        "last_name": "sagan"
                                    }, format = 'json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "henry")
        self.assertEqual(response.data["first_name"], "frank")
        self.assertEqual(response.data["last_name"], "sagan")

    def test_superuser(self):
        '''
            Test the registration, login, put, patch methods, given by drf authorization and viewset code but who knows
        '''
        # partially update the user
        self.client.force_authenticate(user = self.admin)
        # update the user
        response = self.client.put('/api/v1/user/',
                                    {
                                        "username": "henry",
                                        "first_name": "frank",
                                        "last_name": "sagan"
                                    }, format = 'json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "henry")
        self.assertEqual(response.data["first_name"], "frank")
        self.assertEqual(response.data["last_name"], "sagan")
        
        response = self.client.patch('/api/v1/user/',
                                    {
                                        "first_name": "carl",
                                    }, format = 'json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "carl")

    def tearDown(self):
        self.client.logout()
        ApolloUser.objects.get(username='henry').delete()
        self.admin.delete()


class GroupOperations(TestCase):
    '''
        Test group operations such as group creation, discovery and joining, 
        as well as group member operations such as adding and removing members
    '''
    def setUp(self):
        self.client = APIClient()
        self.user = ApolloUser.objects.create_user(username='group-admin', password='supersecret')
        self.newuser = ApolloUser.objects.create_user(username='new-user', password='supersecret')
        self.anotheruser = ApolloUser.objects.create_user(username='another-user', password='supersecret')

    def test_operations(self):
        '''
            Group add, remove, join, leave, discover
        '''
        self.client.force_authenticate(user = self.user)
        # create groups
        response1 = self.client.post('/api/v1/group/',
                                    {
                                        "name": "test-group1",
                                        "group_visibility": "I"
                                    }, format = 'json')
        
        response2 = self.client.post('/api/v1/group/',
                                    {
                                        "name": "test-group2",
                                        "group_visibility": "P"
                                    }, format = 'json')
        
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        # get groups 
        response = self.client.get('/api/v1/group/')
        self.assertTrue(response1.data in response.data)
        self.assertTrue(response2.data in response.data)
        self.assertEqual(len(response.data), 2)
        # delete groups
        response = self.client.delete(f'/api/v1/group/{response1.data["id"]}/')
        self.assertEqual(response.status_code, 204)

    def test_member_add(self):
        '''
            Test adding members to a group
        '''
        self.client.force_authenticate(user = self.user)
        # create group
        response_list = self.client.post('/api/v1/group/',
                                    {
                                        "name": "test-group1",
                                        "group_visibility": "I"
                                    }, format = 'json')
        self.assertEqual(response_list.status_code, 201)
        # get group
        response_list = self.client.get(f'/api/v1/group/{response_list.data["id"]}/')
        self.assertEqual(response_list.status_code, 200)
        # add members
        response = self.client.post(f'/api/v1/group/{response_list.data["id"]}/member/',
                                    {
                                        "new_member": self.newuser.id
                                    }, format = 'json')
        self.assertEqual(response.status_code, 201)
        # get members and check if the new user is in the group
        response = self.client.get(f'/api/v1/group/{response.data["id"]}/member/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.newuser.id in [member['id'] for member in response.data])
        # remove member
        response = self.client.delete(f'/api/v1/group/{response_list.data["id"]}/member/{self.newuser.id}/')
        self.assertEqual(response.status_code, 204)

        # join group
        self.client.force_authenticate(user = self.user)
        response = self.client.post(f'/api/v1/group/{response_list.data["id"]}/member/join/',
                                    {
                                        "invite_token": response_list.data["invite_token"]
                                    }, format = 'json')
        self.assertEqual(response.status_code, 201)
        # user in group
        response = self.client.get(f'/api/v1/group/{response_list.data["id"]}/member/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.id in [member['id'] for member in response.data])

    def test_group_discovery(self):
        '''
            Test group discovery
        '''
        self.client.force_authenticate(user = self.user)
        # create group
        response_list = self.client.post('/api/v1/group/',
                                    {
                                        "name": "test-group1",
                                        "group_visibility": "P"
                                    }, format = 'json')
        self.assertEqual(response_list.status_code, 201)
        # join group
        self.client.force_authenticate(user = self.newuser)
        response = self.client.post(f'/api/v1/group/{response_list.data["id"]}/member/join/', format = 'json')
        self.assertEqual(response.status_code, 201)
        # get group
        response_list = self.client.get(f'/api/v1/group/{response_list.data["id"]}/')
        self.assertEqual(response_list.status_code, 200)
        # user in group
        response = self.client.get(f'/api/v1/group/{response_list.data["id"]}/member/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.newuser.id in [member['id'] for member in response.data])

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.newuser.delete()
        self.anotheruser.delete()