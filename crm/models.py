from django.db import models
from django.core.mail import send_mail
from django.conf import settings

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('sales', 'Salesperson'),
        ('support', 'Support Staff'),
    ]

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # plaintext for now
    email = models.EmailField(null=True, blank=True)  # Make it optional for now
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')]

    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='created_tasks')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.title