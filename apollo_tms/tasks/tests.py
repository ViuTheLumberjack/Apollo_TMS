from django.test import  TestCase
from rest_framework.test import APIClient

from apollo_account.models import ApolloUser, Organization

class CollectionOperations(TestCase):
    '''
        Test operations on the collection view
    '''
    def setUp(self):
        self.client = APIClient()
        self.user = ApolloUser.objects.create_user(username='alternato', password='correntealtatensione')

    def test_operations(self):
        '''
            Test the registration, login, put, patch methods, given by drf authorization and viewset code but who knows
        '''
        self.client.force_authenticate(user=self.user)

        # Create 2 new organizations
        group1 = self.client.post('/api/v1/group/',
                                    {
                                        "name": "Test Group 1",
                                    }, format = 'json').data
        group2 = self.client.post('/api/v1/group/',
                                    {
                                        "name": "Test Group 2",
                                    }, format = 'json').data
        # Create collections
        collection1response = self.client.post('/api/v1/collection/',
                                    {
                                        "name": "Test Collection 1",
                                        "description": "Test Collection 1",
                                        "owner_id": group1['id']
                                    }, format = 'json')
        collection2response = self.client.post('/api/v1/collection/',
                                    {
                                        "name": "Test Collection 2",
                                        "description": "Test Collection 2",
                                        "owner_id": group1['id']
                                    }, format = 'json')
        
        self.assertEqual(collection1response.status_code, 200)
        self.assertEqual(collection2response.status_code, 200)
        self.assertEqual(len(self.client.get('/api/v1/collection/').data), 2) 

    def tearDown(self):
        self.client.logout()
        self.user.delete()

class TaskOperations(TestCase):
    '''
        Test operations on the task view, 
        in particular creation of a task, of subtasks and assignment
    '''
    def setUp(self):
        self.client = APIClient()

    def test_operations(self):
        # register the user to generate the default organization and collection
        regiterresponse = self.client.post('/api/v1/registration/', 
                                    {
                                        "username": "tempocontinuo",
                                        "email": "continuo@continuuo.com",
                                        "password1": "polinomialegradok",
                                        "password2": "polinomialegradok"
                                    }, format = 'json')
        
        self.assertEqual(regiterresponse.status_code, 204, msg=regiterresponse.data)
        # login    
        loginresponse = self.client.post('/api/v1/login/',
                                        {
                                            "username": "tempocontinuo",
                                            "password": "polinomialegradok",
                                        }, format = 'json')
        
        self.assertEqual(loginresponse.status_code, 200, msg=loginresponse.data)
        # set the token for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + loginresponse.data['key'])
        # check default organization and collection
        orgresponse = self.client.get('/api/v1/group/')
        self.assertEqual(len(orgresponse.data), 1)

        collectionresponse = self.client.get('/api/v1/collection/')
        self.assertEqual(len(collectionresponse.data), 1)
        # create a task
        taskresponse = self.client.post(f'/api/v1/collection/{collectionresponse.data[0]["id"]}/tasks/',
                                            {
                                                "resourcetype": "DeadlineTask",
                                                "title": "Test Task",
                                                "description": "Test Task Description",
                                                "due_date": "2021-01-01T00:00:00Z"
                                            }, format = 'json')
            
        self.assertEqual(taskresponse.status_code, 200, msg=taskresponse.data)
        # create a subtask
        subtaskresponse = self.client.post(f'/api/v1/collection/{collectionresponse.data[0]["id"]}/tasks/',
                                            {
                                                "resourcetype": "OneTimeTask",
                                                "title": "Test Subtask",
                                                "description": "Test Subtask Description",
                                                "parent": taskresponse.data['id']
                                            }, format = 'json')
        self.assertEqual(subtaskresponse.status_code, 200, msg=subtaskresponse.data)
        # get the task
        alltasksresponse = self.client.get(f'/api/v1/tasks')
        self.assertEqual(alltasksresponse.status_code, 200, msg=alltasksresponse.data)
        self.assertEqual(len(alltasksresponse.data), 1, msg=alltasksresponse.data)
        # change status of the task
        statusresponse = self.client.post(f'/api/v1/collection/{collectionresponse.data[0]["id"]}/tasks/{taskresponse.data["id"]}/status/',
                                            {
                                                "status": "C"
                                            }, format = 'json')
        self.assertEqual(statusresponse.status_code, 200, msg=statusresponse.data)
        # assign the task to the user, but first add another user 
        userresponse = self.client.post('/api/v1/registration/',
                                    {
                                        "username": "carrello",
                                        "email": "salitaripida@alternato.com",
                                        "password1": "correntealtatensione",
                                        "password2": "correntealtatensione"
                                    }, format = 'json')
        self.assertEqual(userresponse.status_code, 204, msg=userresponse.data)
        # add him to the organization
        new_user = ApolloUser.objects.get(username='carrello')
        adduserresponse = self.client.post(f'/api/v1/group/{orgresponse.data[0]["id"]}/member/',
                                    {
                                        "new_member": new_user.id
                                    }, format = 'json')
        self.assertEqual(adduserresponse.status_code, 201, msg=adduserresponse.data)
        # assign the task
        assignresponse = self.client.post(f'/api/v1/collection/{collectionresponse.data[0]["id"]}/tasks/{taskresponse.data["id"]}/assign/',
                                    {
                                        "user_id": new_user.id
                                    }, format = 'json')
        self.assertEqual(assignresponse.status_code, 200, msg=assignresponse.data)

