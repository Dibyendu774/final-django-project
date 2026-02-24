from django.db import models


class Users(models.Model):
    Name = models.CharField(max_length=50)
    Email = models.EmailField()
    Password = models.CharField(max_length=225)
    Image = models.ImageField(upload_to='user/', default='user.png')
    Role = models.CharField(max_length=50, default='User')
    objects = None


class Products(models.Model):
    name = models.CharField(max_length=255)
    p_des = models.TextField()
    price = models.CharField(max_length=10)
    p_image = models.ImageField(upload_to='product/')
    isCart = models.BooleanField(default=False)
    objects = None


class User_Products(models.Model):
    userid = models.IntegerField()
    pr_id = models.IntegerField()