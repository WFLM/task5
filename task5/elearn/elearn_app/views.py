from django.contrib.auth import user_logged_in
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.authentication import TokenAuthentication

from django.conf import settings

from .models import User, Course, Lecture
from .serializers import UserSerializer, CourseSerializer, LectureSerializer

from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .permission import IsLogged, IsSuperuser, IsTeacher, IsStudent, IsStudentOwn


class CreateUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsSuperuser]
        elif self.action == 'list':
            permission_classes = [IsSuperuser]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsSuperuser]
        elif self.action == 'destroy':
            permission_classes = [IsSuperuser]
        return [permission() for permission in permission_classes]


class LoginView(ViewSet):
    serializer_class = AuthTokenSerializer

    def create(self, request):
        return ObtainAuthToken().post(request)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CourseViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        # permission_classes = [IsSuperuser]
        permission_classes = []
        if self.action == 'create':
            permission_classes += [IsTeacher]
        elif self.action == 'list':
            permission_classes += [IsTeacher | IsStudent]
        elif self.action == 'retrieve':
            permission_classes += [IsTeacher | IsStudent]
        elif self.action in {'update', 'partial_update'}:
            permission_classes += [IsTeacher]
        elif self.action == 'destroy':
            permission_classes += [IsTeacher]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return Course.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return Course.objects.filter(teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return Course.objects.filter(students__email=user)

    # def retrieve(self, request, *args, **kwargs):
    #     user = request.user
    #     queryset = Course.objects.filter(teachers__email=user)
    #     serializer = CourseSerializer
    #     print(queryset)
    #     print(request.user)
    #     return Response(serializer)


class LectureViewSet(ModelViewSet):

    authentication_classes = [TokenAuthentication]
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        # permission_classes = [IsSuperuser]  # reduce + operator.or_ ?
        permission_classes = []
        if self.action == 'create':
            permission_classes += [IsTeacher]
        elif self.action == 'list':
            permission_classes += [IsTeacher | IsStudent]
        elif self.action == 'retrieve':
            permission_classes += [IsTeacher | IsStudent]
        elif self.action in {'update', 'partial_update'}:
            permission_classes += [IsTeacher]
        elif self.action == 'destroy':
            permission_classes += [IsTeacher]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="superusers").exists():
            return Lecture.objects.all()
        elif user.groups.filter(name="teachers").exists():
            return Lecture.objects.filter(course__teachers__email=user)
        elif user.groups.filter(name="students").exists():
            return Lecture.objects.filter(course__students__email=user)
