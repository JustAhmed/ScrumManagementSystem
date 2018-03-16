from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, is_staff=False, is_admin=False, is_active=True):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")
        user_obj = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save()
        return user_obj

    def create_staffuser(self, email, first_name, last_name, password=None):
        user = self.create_user(
            email,
            first_name,
            last_name,
            password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(
            email,
            first_name,
            last_name,
            password,
            is_staff=True,
            is_admin=True
        )

        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=32, blank=True, null=True)
    last_name = models.CharField(max_length=32, blank=True, null=True)
    active = models.BooleanField(default=True)  # Can login
    staff = models.BooleanField(default=False)  # staff user non superuser
    admin = models.BooleanField(default=False)  # superuser

    USERNAME_FIELD = 'email'  # The email field will be the default UserName for the users
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = ['first_name', 'last_name']

    object = UserManager()

    def get_full_name(self):
        return self.first_name + self.last_name

    def get_short_name(self):
        return self.first_name[0] + '.' + self.last_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):  # required from the documentation
        return True

    def has_module_perms(self, app_label):  # required from the documentation
        return True

    def is_staff(self):
        return self.staff

    def is_admin(self):
        return self.admin

    def is_active(self):
        return self.active


class BackLog(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_by = models.ForeignKey(User, related_name='backlogs', on_delete=models.DO_NOTHING, null=True, blank=True)
    start_at = models.DateField(auto_now=True)
    end_at = models.DateField(auto_now_add=False, auto_now=False, null=True)

    def __str__(self):
        return self.name


class Sprint(models.Model):
    name = models.CharField(max_length=25)
    start_at = models.DateField(auto_now_add=True)
    end_at = models.DateField(auto_now_add=False, auto_now=False, null=True)
    state = models.IntegerField(default=1)  # 1: Not started   2: In Progress   3: Done
    backlog = models.ForeignKey(BackLog, related_name='sprints', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    importance = models.IntegerField()
    status = models.IntegerField(default=1)  # 1: Not started   2: In Progress   3: Done
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    start_at = models.DateField(auto_now_add=True)
    end_at = models.DateField(auto_now_add=False, auto_now=False)
    assigned_user = models.ForeignKey(User, related_name='tasks', null=True, on_delete=models.DO_NOTHING)
    sprint = models.ForeignKey(Sprint, related_name='tasks', on_delete=models.CASCADE)

    def __str__(self):
        return self.name