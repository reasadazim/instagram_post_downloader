from django.db import models


class Files(models.Model):
    uid = models.CharField(max_length=100)
    path = models.TextField()
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField()


class Directories(models.Model):
    uid = models.CharField(max_length=100)
    username = models.CharField(max_length=256)
    userid = models.CharField(max_length=256)
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField()
