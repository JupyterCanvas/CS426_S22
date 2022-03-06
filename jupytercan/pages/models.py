# after modifying models.py must migrate changes to database:
# ./manage.py makemigrations
# ./manage.py migrate

from django.db import models

# Create your models here.

# models: https://docs.djangoproject.com/en/3.2/topics/db/models/
class Upload(models.Model):
    description = models.CharField(max_length=100)
    comments = models.TextField(blank=True)
    filename = models.FileField(upload_to='')

    def __str__(self):
        return self.description
