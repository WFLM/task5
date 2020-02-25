import jwt
from django.contrib.auth import user_logged_in
from rest_framework_jwt.serializers import jwt_payload_handler

from django.conf import settings

from .models import User
from .serializers import UserSerializer

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


class CreateUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuthenticateUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
        except KeyError:
            resp = {"error": "'email' and 'password' should be taken."}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            resp = {"error": "cannot authenticate with the given credentials or the account has been deactivated."}
            return Response(resp, status=status.HTTP_403_FORBIDDEN)

        try:
            payload = jwt_payload_handler(user)
            token = jwt.encode(payload, settings.SECRET_KEY)
            user_details = {"name": f"{user.first_name} {user.last_name}",
                            "token": token}
            user_logged_in.send(sender=user.__class__,
                                request=request, user=user)
            return Response(user_details, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
