from django.db import models
from django.contrib.auth.models import User


class MemberNolsatu(models.Model):
    user = models.OneToOneField(User, related_name='nolsatu', on_delete=models.CASCADE)
    id_nolsatu = models.IntegerField()
    avatar = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.id_nolsatu}"
