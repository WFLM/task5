from django.contrib import admin


from .models import Course, Lecture, Homework, HomeworkInstance, HomeworkInstanceComment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    pass


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    pass


@admin.register(HomeworkInstance)
class HomeworkInstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(HomeworkInstanceComment)
class HomeworkInstanceCommentsAdmin(admin.ModelAdmin):
    pass
