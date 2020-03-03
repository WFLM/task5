from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from .permission import IsSuperuser, IsTeacher, IsStudent
from .models import User, Course, Lecture, Homework, HomeworkInstance, HomeworkInstanceComment, HomeworkInstanceMark
from .serializers import (
    UserSerializer, CourseSerializer, LectureSerializer, HomeworkSerializer,
    HomeworkInstanceSerializer, HomeworkInstanceCommentSerializer, HomeworkInstanceMarkSerializer
)


class CreateUserAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserSerializer, tags=("Accounting",))
    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsSuperuser()]
        elif self.action in {"list", "retrieve"}:
            return [(IsSuperuser | IsTeacher)()]


class LoginView(ViewSet):
    serializer_class = AuthTokenSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=AuthTokenSerializer, tags=("Accounting",))
    def create(self, request):
        return ObtainAuthToken().post(request)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=("Accounting",))
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CourseViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [(IsSuperuser | IsTeacher)()]
        elif self.action in {"list", "retrieve"}:
            return [(IsSuperuser | IsTeacher | IsStudent)()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return Course.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return Course.objects.filter(teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return Course.objects.filter(students__email=user)


class LectureViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = LectureSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", " destroy"}:
            return [(IsSuperuser | IsTeacher)()]
        elif self.action in {"list", "retrieve"}:
            return [(IsSuperuser | IsTeacher | IsStudent)()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return Lecture.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return Lecture.objects.filter(course__teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return Lecture.objects.filter(course__students__email=user)


class HomeworkViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = HomeworkSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [(IsSuperuser | IsTeacher)()]
        elif self.action in {"list", "retrieve"}:
            return [(IsSuperuser | IsTeacher | IsStudent)()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return Homework.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return Homework.objects.filter(lecture__course__teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return Homework.objects.filter(lecture__course__students__email=user)


class HomeworkInstanceViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = HomeworkInstanceSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update"}:
            return [IsStudent()]
        elif self.action in {"list", "retrieve"}:
            return [(IsSuperuser | IsTeacher | IsStudent)()]
        elif self.action == 'destroy':
            return [IsSuperuser()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return HomeworkInstance.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return HomeworkInstance.objects.filter(homework__lecture__course__teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return HomeworkInstance.objects.filter(homework__lecture__course__students__email=user)


class HomeworkInstanceCommentViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = HomeworkInstanceCommentSerializer

    def get_permissions(self):
        return [(IsSuperuser | IsTeacher | IsStudent)()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return HomeworkInstanceComment.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return HomeworkInstanceComment.objects.filter(
                homework_instance__homework__lecture__course__teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return HomeworkInstanceComment.objects.filter(homework_instance__student_id=user)


class HomeworkInstanceMarkViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = HomeworkInstanceMarkSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [(IsSuperuser | IsTeacher)()]
        elif self.action in {"list", "retrieve"}:
            return [(IsSuperuser | IsTeacher | IsStudent)()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return HomeworkInstanceMark.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return HomeworkInstanceMark.objects.filter(
                homework_instance__homework__lecture__course__teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return HomeworkInstanceMark.objects.filter(homework_instance__student_id=user)
