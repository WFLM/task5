from django.contrib import admin

from .models import User, Course, Lecture, Homework, HomeworkInstance, HomeworkInstanceMark, HomeworkInstanceComment
from .forms import CourseForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "user_groups"
    )

    def user_groups(self, obj):
        return ','.join([g.name for g in obj.groups.all()]) if obj.groups.count() else ''


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teachers":
            kwargs["queryset"] = User.objects.filter(groups__name='teachers')

        elif db_field.name == "students":
            kwargs["queryset"] = User.objects.filter(groups__name='students')

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    pass


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    pass


# @admin.register(HomeworkInstanceMark)
class HomeworkInstanceMarkAdmin(admin.TabularInline):
    model = HomeworkInstanceMark
    fields = (
        "mark",
    )


# @admin.register(HomeworkInstanceComment)
class HomeworkInstanceCommentsAdmin(admin.TabularInline):
    model = HomeworkInstanceComment


@admin.register(HomeworkInstance)
class HomeworkInstanceAdmin(admin.ModelAdmin):
    inlines = (HomeworkInstanceMarkAdmin, HomeworkInstanceCommentsAdmin)
