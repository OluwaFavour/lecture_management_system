import uuid

from django.contrib.auth import authenticate, login, logout

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from .models import Session, User
from .permissions import IsLecturer, IsClassRep
from .serializers import LoginSerializer, UserSerializer


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "login":
            return LoginSerializer
        if self.action == "register":
            return UserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["login", "register"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @extend_schema(
        request=LoginSerializer,
        responses={status.HTTP_200_OK: LoginSerializer},
        tags=["auth"],
    )
    @action(detail=False, methods=["POST"])
    def login(self, request):
        """
        Login a user and create a new session for the user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data.pop("username"),
            password=serializer.validated_data.pop("password"),
        )
        if not user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )
        login(request, user)

        # Create or update the session
        session_token = str(uuid.uuid4())
        is_first_login = not Session.objects.filter(user=user).exists()

        custom_session, _ = Session.objects.update_or_create(
            user=user,
            defaults={
                "token": session_token,
                "is_current": True,
                "is_first_login": is_first_login,
            },
        )

        # Store session token in the request session
        request.session["session_token"] = session_token
        request.session["user_id"] = user.pk

        return Response(LoginSerializer(custom_session).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=OpenApiTypes.NONE,
        responses={status.HTTP_204_NO_CONTENT: OpenApiTypes.NONE},
        tags=["auth"],
    )
    @action(detail=False, methods=["POST"])
    def logout(self, request):
        """
        Logout a user and invalidate the current session.
        """
        # Invalidate current session
        Session.objects.filter(user=request.user, is_current=True).update(
            is_current=False
        )

        # Clear session token from the request session
        logout(request)
        request.session.flush()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=UserSerializer,
        responses={status.HTTP_201_CREATED: UserSerializer},
        tags=["auth"],
    )
    @action(detail=False, methods=["POST"])
    def register(self, request):
        """
        Register a new user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["users"])
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["get_all_lecturers", "get_lecturer"]:
            return [IsClassRep]
        if self.action in ["get_all_classreps", "get_class_rep"]:
            return [IsLecturer]
        return super().get_permissions()

    @extend_schema(
        request=OpenApiTypes.NONE,
        responses={status.HTTP_200_OK: UserSerializer},
    )
    @action(detail=False, methods=["GET"])
    def me(self, request):
        """
        Retrieve the current user.
        """
        user = request.user
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_all_lecturers(self, request):
        lecturers = self.get_queryset().filter(is_lecturer=True)
        serializer = self.get_serializer(data=lecturers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="get_lecturer/(?P<lecturer_id>\d+)")
    def get_lecturer(self, request, lecturer_id=None):
        lecturer = self.get_queryset().filter(pk=lecturer_id, is_lecturer=True)
        serializer = self.get_serializer(data=lecturer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_all_classreps(self, request):
        students = self.get_queryset().filter(is_student=True, is_class_rep=True)
        serializer = self.get_serializer(data=students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="get_student/(?P<class_rep_id>\d+)")
    def get_class_rep(self, request, class_rep_id=None):
        student = self.get_queryset().filter(
            pk=class_rep_id, is_student=True, is_class_rep=True
        )
        serializer = self.get_serializer(data=student)
        return Response(serializer.data, status=status.HTTP_200_OK)
