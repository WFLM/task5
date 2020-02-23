from django.db import models
from django.contrib.auth.models import User


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
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, null=False)
    text = models.TextField(null=False)

    def __str__(self):
        return f"Homework \"{self.title}\" from lecture \"{self.lecture.title}\""


class HomeworkInstance(models.Model):
    class Meta:
        unique_together = (("homework", "student"),)

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


from . import groups  # workaround
