from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.

class ImageAppUserManager(BaseUserManager):
    def create_user(self, email, dob, nickname, password=None):
        user = self.model(email=email, dob=dob, nickname=nickname)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, dob, nickname, password):
        user = self.model(email=email, dob=dob, nickname=nickname)
        user.is_admin = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class ImageAppUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    nickname = models.CharField(max_length=100, unique=True)
    dob = models.DateField()
    date_joined = models.DateTimeField(default=timezone.now())
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = ImageAppUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dob', 'nickname']

    

    def get_full_name(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def __unicode__(self):
        return self.nickname

    def is_staff(self):
        return self.is_admin
    property(is_staff)
