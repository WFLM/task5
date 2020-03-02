from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.db import transaction

# User- should be rewritten


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """

        if not email:
            raise ValueError('The given email must be set')
        try:
            with transaction.atomic():
                group = extra_fields.pop("group")
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                user.groups.set([Group.objects.get(name=group)])
                return user
        except:
            raise

    def create_user(self, email, password=None,  **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('group', 'superusers')
        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=40, unique=True)
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self


class Course(models.Model):
    title = models.CharField(max_length=128, null=False, unique=True)
    teachers = models.ManyToManyField(User, related_name="course_teachers")
    students = models.ManyToManyField(User, related_name="course_students", blank=True)

    def __str__(self):
        return f"Course \"{self.title}\""


class Lecture(models.Model):
    class Meta:
        unique_together = (("course_id", "title"),)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, null=False)
    file = models.FileField(upload_to="lectures/", null=False)

    def __str__(self):
        return f"Lecture \"{self.title}\""


class Homework(models.Model):
    class Meta:
        unique_together = (("lecture_id", "title"),)

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, null=False)
    text = models.TextField(null=False)

    def __str__(self):
        return f"Homework \"{self.title}\" from lecture \"{self.lecture.title}\""


class HomeworkInstance(models.Model):
    class Meta:
        unique_together = (("homework_id", "student_id"),)

    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    file = models.FileField(upload_to="done_homeworks/", null=True)
    is_done = models.BooleanField(default=False)
    # mark = models.SmallIntegerField(null=True)

    def __str__(self):
        return f"Homework: {self.homework.title} by {self.student}"


class HomeworkInstanceMark(models.Model):
    homework_instance = models.OneToOneField(HomeworkInstance, on_delete=models.CASCADE)
    mark = models.SmallIntegerField(null=True)

    def __str__(self):
        return f"{self.homework_instance} : {self.mark}"


class HomeworkInstanceComment(models.Model):
    homework_instance = models.ForeignKey(HomeworkInstance, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    body = models.TextField(null=False, blank=False)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment: {self.body} by {self.author}"


# from . import groups  # workaround
