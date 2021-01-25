from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.templatetags.static import static
from model_utils import Choices


class MemberNolsatu(models.Model):
    ROLE = Choices(
        (1, 'student', 'Student'),
        (2, 'trainer', 'Trainer'),
        (3, 'company', 'Company'),
        (4, 'vendor', 'Vendor'),
    )

    user = models.OneToOneField(User, related_name='nolsatu', on_delete=models.CASCADE)
    id_nolsatu = models.IntegerField()
    role = models.PositiveIntegerField(choices=ROLE, blank=True, null=True)
    avatar = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.id_nolsatu} - {self.role}"

    def get_avatar(self):
        if self.avatar:
            avatar = self.avatar
        else:
            avatar = settings.HOST + static('website/images/avatar_placeholder.png')

        return avatar
