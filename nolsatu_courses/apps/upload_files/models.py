from django.db import models


class UploadFile(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="uploads/", max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
