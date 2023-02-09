from django.db import models


class Bug(models.Model):

    class Status(models.TextChoices):
        RESOLVED = 'resolved'
        UNRESOLVED = 'unresolved'

    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNRESOLVED)
    assignee_id = models.CharField(max_length=10)

    def __str__(self):
        return self.title


class Comment(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
