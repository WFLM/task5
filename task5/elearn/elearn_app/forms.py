from django.forms import ModelForm, ValidationError
from django.contrib.auth.models import Group
from .models import Course


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = (
            "title",
            "teachers",
            "students"
        )

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Title too short. Use clearer title.")
        return title

    def clean_teachers(self):
        users = self.cleaned_data["teachers"]
        users_count = users.count()
        teachers = users.filter(groups__name='teachers')
        teachers_count = teachers.count()

        if users_count == teachers_count:
            return teachers
        else:
            raise ValidationError("Not all got users are teachers.", code="invalid")

    def clean_students(self):
        users = self.cleaned_data["students"]
        users_count = users.count()
        students = users.filter(groups__name="students")
        students_count = students.count()

        if users_count == students_count:
            return students
        else:
            raise ValidationError("Not all got users are students.", code="invalid")
