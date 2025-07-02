from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.contrib.auth import get_user_model

class InstitutionManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError("The Name must be set")
        user = self.model(name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(name, password, **extra_fields)



class Institution(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    objects = InstitutionManager()

    def __str__(self):
        return self.name
 
class Teacher(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.institution.name})"

class Student(models.Model):
    name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=100)
    student_class = models.CharField(max_length=20, choices=[
        ('Form 1', 'Form 1'),
        ('Form 2', 'Form 2'),
        ('Form 3', 'Form 3'),
        ('Form 4', 'Form 4')
    ])
    institution = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 👈 this points to your Institution model
        on_delete=models.CASCADE,
        related_name='students'
    )

    class Meta:
        unique_together = ('admission_number', 'institution')

    def __str__(self):
        return f"{self.name} - {self.admission_number}"



class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(
        max_length=100,
        choices=[
            ('mathematics', 'Mathematics'),
            ('english', 'English'),
            ('kiswahili', 'Kiswahili'),
            ('history', 'History'),
            ('geography', 'Geography'),
            ('cre', 'CRE'),
            ('business', 'Business'),
            ('agriculture', 'Agriculture'),
        ],
        default='mathematics'
    )
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'subject')

class StudentResult(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    mathematics = models.IntegerField(default=0)
    english = models.IntegerField(default=0)
    kiswahili = models.IntegerField(default=0)
    history = models.IntegerField(default=0)
    geography = models.IntegerField(default=0)
    cre = models.IntegerField(default=0)
    business = models.IntegerField(default=0)
    agriculture = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.adm_no} Results"




