from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    title = models.CharField(max_length=128, null=False)
    teachers = models.ManyToManyField(User, related_name="course_teachers")
    students = models.ManyToManyField(User, related_name="course_students")


class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, null=False)
    file = models.FileField(upload_to='lectures/', null=False)


class Homework(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, null=False)
    text = models.TextField(null=False)


class HomeworkInstance(models.Model):
    class Meta:
        unique_together = (('homework', 'student'),)

    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    uploaded_work = models.FileField(upload_to='done_homeworks/', null=True)
    is_done = models.BooleanField(default=False)
    mark = models.SmallIntegerField(null=True)


class HomeworkInstanceComments(models.Model):
    homework_instance = models.ForeignKey(HomeworkInstance, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now=True)
    body = models.TextField(null=False)
