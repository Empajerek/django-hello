from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import BackgroundImage, Route, Point
from django.core.files.uploadedfile import SimpleUploadedFile

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.bg_image = BackgroundImage.objects.create(
            name='Test Image',
            image=SimpleUploadedFile('test.jpg', b'content')
        )

    def test_route_creation(self):
        route = Route.objects.create(
            user=self.user,
            background=self.bg_image,
            name='Test Route'
        )
        self.assertEqual(route.user.username, 'testuser')
        self.assertEqual(route.background.name, 'Test Image')
        self.assertEqual(str(route), 'Test Route (testuser)')

    def test_point_ordering(self):
        route = Route.objects.create(user=self.user, background=self.bg_image)
        p1 = Point.objects.create(route=route, x=10, y=20, order=2)
        p2 = Point.objects.create(route=route, x=30, y=40, order=3)
        p3 = Point.objects.create(route=route, x=50, y=60, order=1)
        self.assertEqual(p1.x, 10)
        self.assertEqual(p2.y, 40)
        self.assertEqual(p3.order, 1)

class WebInterfaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.bg_image = BackgroundImage.objects.create(
            name='Test Image',
            image=SimpleUploadedFile('test.jpg', b'content')
        )
        self.route = Route.objects.create(
            user=self.user,
            background=self.bg_image,
            name='Test Route'
        )

    def test_authentication_required(self):
        urls = [
            reverse('route_list'),
            reverse('create_route'),
            reverse('route_detail', args=[self.route.id]),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_route_management(self):
        self.client.login(username='testuser', password='testpass')
        
        # Test route list
        response = self.client.get(reverse('route_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        
        # Test add point
        response = self.client.post(
            reverse('route_detail', args=[self.route.id]),
            {'x': 100, 'y': 200}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.route.points.count(), 1)
        
        # Test delete point
        point = self.route.points.first()
        response = self.client.post(
            reverse('delete_point', args=[self.route.id, point.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.route.points.count(), 0)

class APITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        self.bg_image = BackgroundImage.objects.create(
            name='Test Image',
            image=SimpleUploadedFile('test.jpg', b'content')
        )
        
        self.route = Route.objects.create(
            user=self.user1,
            background=self.bg_image,
            name='Test Route'
        )
        self.point = Point.objects.create(route=self.route, x=10, y=20)

    def test_api_authentication(self):
        response = self.client.get('/api/routes/')
        self.assertEqual(response.status_code, 403)

    def test_route_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        
        # Test create route
        response = self.client.post('/api/routes/', {
            'name': 'New Route',
            'background': self.bg_image.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Route.objects.count(), 2)
        
        # Test list routes
        response = self.client.get('/api/routes/')
        self.assertEqual(len(response.data), 2)
        
        # Test access other user's route
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        response = self.client.get(f'/api/routes/{self.route.id}/')
        self.assertEqual(response.status_code, 404)

    def test_point_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        
        # Add point
        response = self.client.post(
            f'/api/routes/{self.route.id}/points/',
            {'x': 30, 'y': 40}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.route.points.count(), 2)
        
        # Delete point
        response = self.client.delete(
            f'/api/routes/{self.route.id}/points/{self.point.id}/'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.route.points.count(), 1)

    def test_validation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        
        # Test invalid coordinates
        response = self.client.post(
            f'/api/routes/{self.route.id}/points/',
            {'x': 'abc', 'y': 40}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('x', response.data)
