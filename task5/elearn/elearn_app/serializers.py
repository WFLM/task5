from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from .models import User, Group, Course, Lecture, Homework, HomeworkInstance, HomeworkInstanceComment, \
    HomeworkInstanceMark


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="ID", required=False)
    email = serializers.EmailField(
        max_length=40, required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(allow_blank=True, max_length=30, required=True)
    last_name = serializers.CharField(allow_blank=True, max_length=30, required=True)
    date_joined = serializers.ReadOnlyField()
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    group = serializers.CharField(write_only=True, required=True)

    user_group = serializers.SerializerMethodField()   # To get "group" in serializer.data then.

    _GROUP_NAMES = tuple(str(group) for group in Group.objects.all())

    def validate_group(self, value):
        if value == "superusers":
            raise serializers.ValidationError({"detail": ["Superuser cannot be created this way."]})
        elif value not in self._GROUP_NAMES:
            raise serializers.ValidationError({"group": [f"Group {value} not exists."]})
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
        fields = (
            "id", "title", "teachers", "students",
            "teachers_emails", "students_emails",
            "course_teachers", "course_students"
        )
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
            raise serializers.ValidationError({"teachers_email": [f"Teacher with email {email_as_text} not exists."]})
        else:
            return users_querysets

    def validate_students_emails(self, value):
        try:
            users_querysets = []
            for email_as_text in value:
                users_querysets.append(User.objects.get(email=email_as_text, groups__name="students"))
        except User.DoesNotExist:
            raise serializers.ValidationError({"students_email": [f"Student with email {email_as_text} not exists."]})
        else:
            return users_querysets

    def create(self, validated_data):
        user = self.context["request"].user

        teachers = validated_data["teachers_emails"] if "teachers_emails" in validated_data else []
        students = validated_data["students_emails"] if "students_emails" in validated_data else []

        teachers.append(user)

        course = Course(title=validated_data["title"])
        course.save()
        course.teachers.set(teachers)
        course.students.set(students)
        return course


class LectureSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Lecture

        fields = ("id", "title", "file", "course", "course_name")

        extra_kwargs = {
            "id": {"required": False},
            "course": {"required": False}
        }

    def validate_course_name(self, value):
        if Course.objects.filter(title=value).exists():
            return value  # str
        else:
            raise serializers.ValidationError({"course_name": [f"course_name {value} not exists."]})

    def _get_course(self):
        if "course" in self.validated_data:
            return self.validated_data["course"]
        elif "course_name" in self.validated_data:
            return Course.objects.get(title=self.validated_data["course_name"])

        else:
            raise serializers.ValidationError({
                "course": ["This field or course_name are required."],
                "course_name": ["This field or course are required."]
            })

    def _unique_together_courseid_title_validator(self, course, title):
        if Lecture.objects.filter(course=course, title=title).exists():
            raise serializers.ValidationError({
                "detail": ["The fields 'title' and 'course' must be unique together."],
            })

    def _check_users_permissions(self, course):
        user = self.context["request"].user
        if not course.teachers.filter(email=user).exists():
            raise serializers.ValidationError({"detail": ["Access denied."]})

    def create(self, validated_data):
        course = self._get_course()
        self._check_users_permissions(course)
        title = validated_data["title"]
        self._unique_together_courseid_title_validator(course, title)

        lecture = Lecture(
            title=validated_data["title"],
            file=validated_data["file"],
            course=course
        )
        lecture.save()
        return lecture

    def update(self, instance, validated_data):
        course = instance.course
        self._check_users_permissions(course)
        title = validated_data.get("title", instance.title)
        if title != instance.title:
            self._unique_together_courseid_title_validator(course, title)
        instance.title = title
        instance.file = validated_data.get("file", instance.file)
        instance.save()
        return instance


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ("id", "title", "text", "lecture")

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Homework.objects.all(),
                fields=("title", "lecture")
            )
        ]

    def _check_users_permissions(self, lecture):
        user = self.context["request"].user
        if not lecture.course.teachers.filter(email=user).exists():
            raise serializers.ValidationError({"detail": ["Access denied."]})

    def create(self, validate_data):
        lecture = validate_data["lecture"]
        self._check_users_permissions(lecture)
        homework = Homework(
            title=validate_data["title"],
            text=validate_data["text"],
            lecture=lecture
        )
        homework.save()
        return homework

    def update(self, instance, validated_data):
        lecture = instance.lecture
        self._check_users_permissions(lecture)
        instance.title = validated_data.get("title", instance.title)
        instance.text = validated_data.get("text", instance.text)
        instance.save()
        return instance


class HomeworkInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeworkInstance

        fields = ("id", "homework", "student", "file", "is_done")
        extra_kwargs = {
            "student": {"required": False},
            "homework": {"required": False}
        }

    def _get_student_id(self):
        user = self.context["request"].user

        if user.groups.filter(name="students").exists():
            student_id = user.id
            return student_id

        elif "student" in self.validated_data:
            student_id = self.validated_data["student"].id
            return student_id

        else:
            raise serializers.ValidationError(
                {
                    "detail": ["auth user must be a student or student field must be defined."],
                    "student": ["auth user must be a student or student field must be defined."]
                }
            )

    def _get_homework_id(self):  # without it update-function always wants to get "homework" but this is immutable field
        if "homework" in self.validated_data:
            return self.validated_data["homework"].id
        else:
            return serializers.ValidationError({"homework": ["This field is required."]})

    def _unique_together_homeworkid_studentid_validator(self, homework_id, student_id):
        if HomeworkInstance.objects.filter(homework_id=homework_id, student_id=student_id).exists():
            raise serializers.ValidationError({
                "detail": ["The fields 'homework_id' and 'student_id' must be unique together. "
                           "(This homework instance already exists)."],
            })

    def create(self, validated_data):
        student_id = self._get_student_id()
        homework_id = self._get_homework_id()
        self._unique_together_homeworkid_studentid_validator(homework_id, student_id)

        homework_instance = HomeworkInstance(
            homework_id=homework_id,
            student_id=student_id,
            file=validated_data["file"] if "file" in validated_data else None,
            is_done=validated_data["is_done"] if "is_done" in validated_data else False,
        )
        homework_instance.save()
        return homework_instance

    def update(self, instance, validated_data):
        instance.file = validated_data.get("file", instance.file)
        instance.is_done = validated_data.get("is_done", instance.is_done)
        instance.save()
        return instance


class HomeworkInstanceCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkInstanceComment

        fields = ("id", "homework_instance", "author", "created_on", "body")

        extra_kwargs = {
            "homework_instance": {"required": False},
            "author": {"required": False, "read_only": True},
            "created_on": {"read_only": True}
        }

    def _get_author_id(self, homework_instance_id):
        user = self.context["request"].user

        if user.groups.filter(name="students").exists():
            if HomeworkInstance.objects.filter(id=homework_instance_id, student_id=user.id).exists():
                return user.id
            else:
                raise serializers.ValidationError({"detail": ["Access denied."]})

        elif user.groups.filter(name="teachers").exists():
            if HomeworkInstance.objects.filter(homework__lecture__course__students__email=user).exists():
                return user.id
            else:
                raise serializers.ValidationError({"detail": ["Access denied. T"]})

    def _get_homework_instance_id(self):  # without it update-function always wants to get "homework_instance" but this is immutable field
        if "homework_instance" in self.validated_data:
            return self.validated_data["homework_instance"].id
        else:
            raise serializers.ValidationError({"homework_instance": ["This field is required."]})

    def create(self, validated_data):

        homework_instance_id = self._get_homework_instance_id()
        author_id = self._get_author_id(homework_instance_id)

        homework_instance_comment = HomeworkInstanceComment(
            homework_instance_id=homework_instance_id,
            author_id=author_id,
            body=validated_data["body"]
        )
        homework_instance_comment.save()
        return homework_instance_comment

    def update(self, instance, validated_data):
        instance.body = validated_data.get("body", instance.body)
        instance.save()
        return instance


class HomeworkInstanceMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkInstanceMark

        fields = ("id", "mark")

