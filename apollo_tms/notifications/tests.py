from django.test import TestCase
from rest_framework.test import APIClient

from apollo_account.models import ApolloUser
# Create your tests here.

class UserOperations(TestCase):
    '''
        Test operations on the notifications view
    '''
    def setUp(self):
        self.clientowner = APIClient()
        self.client = APIClient()

    def test_operations(self):
        '''
            Test the notifications insertion, the filtering, and the status change
        '''
        # add a user and perform some operations that generate notifications
        self.clientowner.post('/api/v1/registration/',
                                    {
                                        "username": "john",
                                        "email": "john@lennon.com",
                                        "password1": "yokoonoismylife",
                                        "password2": "yokoonoismylife"
                                    }, format = 'json')
        
        response = self.clientowner.post('/api/v1/login/', 
                                    {
                                        "username":"john", 
                                        "password":"yokoonoismylife"
                                    }, format = 'json')
        # expect a 200 response and add token to header
        self.assertEqual(response.status_code, 200)
        self.clientowner.credentials(HTTP_AUTHORIZATION='Token ' + response.data['key'])

        # register a new user and login 
        self.client.post('/api/v1/registration/',
                                    {
                                        "username": "paul",
                                        "email": "paul@mc.com",
                                        "password1": "paolocaffelatte",
                                        "password2": "paolocaffelatte"
                                    }, format = 'json')
        
        response = self.client.post('/api/v1/login/', 
                                    {
                                        "username":"paul", 
                                        "password":"paolocaffelatte"
                                    }, format = 'json')
        # expect a 200 response and add token to header
        self.assertEqual(response.status_code, 200, msg=response.data)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['key'])

        # create a group and add the user to it
        responsegroup = self.clientowner.post('/api/v1/group/',
                                    {
                                        "name": "Beatles Group",
                                        "group_visibility": "P"
                                    }, format = 'json')
        self.assertEqual(response.status_code, 200)
        
        # add the user to the group, the group is public so the user is added automatically
        joinresponse = self.client.post(f'/api/v1/group/{responsegroup.data["id"]}/member/join/')
        self.assertEqual(joinresponse.status_code, 201)
        
        # verify notification has been created
        ownernotif = self.clientowner.get('/api/v1/notifications/')
        self.assertEqual(ownernotif.status_code, 200, msg=ownernotif.data)
        self.assertEqual(len(ownernotif.data), 1, msg=ownernotif.data)

        # read the notification and verify it has been read
        readresponse = self.clientowner.post(f'/api/v1/notifications/{ownernotif.data[0]["id"]}/read/')
        self.assertEqual(readresponse.status_code, 200, msg=readresponse.data)
        ownernotif = self.clientowner.get('/api/v1/notifications/')
        self.assertEqual(ownernotif.status_code, 200, msg=ownernotif.data)
        self.assertEqual(len(ownernotif.data), 1, msg=ownernotif.data)
        self.assertEqual(ownernotif.data[0]['read'], True, msg=ownernotif.data)

        # verify other notifications are created, like on task creation and assignment
        # get collection id
        collectionresponse = self.clientowner.get('/api/v1/collection/')
        self.assertEqual(collectionresponse.status_code, 200, msg=collectionresponse.data)
        collection_id = [data["id"] for data in collectionresponse.data if data["name"] == "Beatles Group's collection"]
        # create a task
        taskresponse = self.clientowner.post(f'/api/v1/collection/{collection_id[0]}/tasks/',
                                    {
                                        "title": "Task 1",
                                        "description": "Task 1 description",
                                        "task_status": "N",
                                        "progress": 0,
                                        "parent": None,
                                        "resourcetype": "OneTimeTask"
                                    }, format = 'json')
        self.assertEqual(taskresponse.status_code, 200, msg=taskresponse.data)
        # verify notification has been created for the client
        clientnotif = self.client.get('/api/v1/notifications/')
        self.assertEqual(clientnotif.status_code, 200, msg=clientnotif.data)
        # task creation does not generate a notification
        self.assertEqual(len(clientnotif.data), 0, msg=clientnotif.data)
        # assign the task to the client
        # short hand for retrieving the user from the group members
        client_user = ApolloUser.objects.get(username="paul")
        assignresponse = self.clientowner.post(f'/api/v1/collection/{collection_id[0]}/tasks/{taskresponse.data["id"]}/assign/',
                                    {
                                        "user_id": client_user.id
                                    }, format = 'json')
        self.assertEqual(assignresponse.status_code, 200, msg=assignresponse.data)
        # verify notification has been created for the client
        clientnotif = self.client.get('/api/v1/notifications/')
        self.assertEqual(clientnotif.status_code, 200, msg=clientnotif.data)
        self.assertEqual(len(clientnotif.data), 1,  msg=clientnotif.data)

        #complete the task and verify notification has been created for the owner
        completetaskresponse = self.client.post(f'/api/v1/collection/{collection_id[0]}/tasks/{taskresponse.data["id"]}/status/', 
                                                {
                                                    "status": "C"
                                                }, format = 'json')
        self.assertEqual(completetaskresponse.status_code, 200, msg=completetaskresponse.data)
        ownernotif = self.clientowner.get('/api/v1/notifications/')
        self.assertEqual(ownernotif.status_code, 200, msg=ownernotif.data)
        self.assertEqual(len(ownernotif.data), 2, msg=ownernotif.data)