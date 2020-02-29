from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, Group, Course, Lecture, Homework


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', required=False)
    email = serializers.EmailField(max_length=40, required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(allow_blank=True, max_length=30, required=True)
    last_name = serializers.CharField(allow_blank=True, max_length=30, required=True)
    date_joined = serializers.ReadOnlyField()
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    group = serializers.CharField(write_only=True, required=True)

    user_group = serializers.SerializerMethodField()   # To get "group" in serializer.data then.

    _GROUP_NAMES = tuple(str(group) for group in Group.objects.all())
    def validate_group(self, value):

        if value == "superusers":
            raise serializers.ValidationError(f"Superuser cannot be created this way.")
        elif value not in self._GROUP_NAMES:
            raise serializers.ValidationError(f"Group {value} doesn't exist.")
        else:
            return value

    def get_user_group(self, obj):
        return str(obj.groups.all()[0])

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        group_queryset = Group.objects.get(name=validated_data["group"])

        user.save()
        user.groups.set((group_queryset,))
        return user


class CourseSerializer(serializers.ModelSerializer):
    teachers_emails = serializers.ListField(write_only=True, required=False)
    students_emails = serializers.ListField(write_only=True, required=False)

    course_teachers = serializers.SerializerMethodField()
    course_students = serializers.SerializerMethodField()

    def get_course_teachers(self, obj):
        return [str(teacher) for teacher in obj.teachers.all()]

    def get_course_students(self, obj):
        return [str(student) for student in obj.students.all()]

    class Meta:
        model = Course
        fields = ['id', 'title', 'teachers', 'students',
                  'teachers_emails', 'students_emails',
                  'course_teachers', 'course_students']
        extra_kwargs = {
            "id": {"required": False},
            "teachers": {"required": False, "write_only": True},
            "students": {"required": False, "write_only": True}
        }

    def validate_teachers_emails(self, value):
        try:
            users_querysets = []
            for email_as_text in value:
                users_querysets.append(User.objects.get(email=email_as_text, groups__name="teachers"))
        except User.DoesNotExist:
            raise serializers.ValidationError(f"Teacher with email {email_as_text} doesn't exist.")
        else:
            return users_querysets

    def validate_students_emails(self, value):
        try:
            users_querysets = []
            for email_as_text in value:
                users_querysets.append(User.objects.get(email=email_as_text, groups__name="students"))
        except User.DoesNotExist:
            raise serializers.ValidationError(f"Student with email {email_as_text} doesn't exist.")
        else:
            return users_querysets

    def create(self, validated_data):
        user = self.context["request"].user

        teachers = validated_data["teachers_emails"] if "teachers_emails" in validated_data else []
        students = validated_data["students_emails"] if "students_emails" in validated_data else []

        teachers.append(user)

        course = Course(title=validated_data['title'])
        course.save()
        course.teachers.set(teachers)
        course.students.set(students)
        return course


class LectureSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Lecture
        fields = [
            'id', 'title', 'file', 'course_id',
            'course_name'
        ]

        extra_kwargs = {
            "id": {"required": False},
            "course_id": {"required": False},
            # "course_name": {"required": False, "write_only": True},
            "title": {"validators": [UniqueValidator(queryset=Lecture.objects.all())]}
        }

    def validate_course_name(self, value):
        if Course.objects.filter(title=value).exists():
            return value  # str
        else:
            raise serializers.ValidationError(f"Course {value} doesn't exist.")

    def create(self, validated_data):
        if 'course_id' in validated_data:
            course_id = validated_data['course_id']
        elif 'course_name' in validated_data:
            course_id = Course.objects.get(title=validated_data['course_name']).id
        else:
            raise

        lecture = Lecture(
            title=validated_data['title'],
            file=validated_data['file'],
            course_id=course_id
        )
        lecture.save()
        return lecture


class HomeworkSerializer(serializers.ModelSerializer):
    lecture_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Homework
        fields = [
            'id', 'title', 'text', 'lecture_id',
            'lecture_name'
        ]

        extra_kwargs = {
            "id": {"required": False},
            "lecture_id": {"required": False},
            # "lecture_name": {"required": False, "write_only": True},
            "title": {"validators": [UniqueValidator(queryset=Homework.objects.all())]}
        }

    def validate_lecture_name(self, value):
        if Lecture.objects.filter(title=value).exists():
            return value  # str
        else:
            raise serializers.ValidationError(f"Lecture {value} doesn't exist.")

    def create(self, validated_data):
        if 'lecture_id' in validated_data:
            lecture_id = validated_data['lecture_id']
        elif 'lecture_name' in validated_data:
            lecture_id = Lecture.objects.get(title=validated_data['lecture_name']).id
        else:
            raise

        homework = Homework(
            title=validated_data['title'],
            text=validated_data['text'],
            lecture_id=lecture_id
        )
        homework.save()
        return homework
