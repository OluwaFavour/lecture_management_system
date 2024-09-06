import uuid

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    PolymorphicProxySerializer,
)

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from .models import Session, User
from .permissions import IsLecturer, IsClassRep, IsRegistrationOfficer
from .serializers import (
    LoginSerializer,
    StudentSerializer,
    LecturerSerializer,
)


@extend_schema(tags=["auth"])
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "login":
            return LoginSerializer
        if self.action == "register_lecturer":
            return LecturerSerializer
        if self.action == "register_student":
            return StudentSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "logout":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        request=LoginSerializer,
        responses={status.HTTP_200_OK: LoginSerializer},
        summary="Login a user and create a new session for the user.",
        description="Login a user and create a new session for the user.",
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
        summary="Logout a user and invalidate the current session.",
        description="Logout a user and invalidate the current session.",
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
        request=LecturerSerializer,
        responses={status.HTTP_201_CREATED: LecturerSerializer},
        summary="Register a new lecturer.",
        description="Register a new lecturer. Lecturers are users who are responsible for teaching and managing courses.",
    )
    @action(detail=False, methods=["POST"])
    def register_lecturer(self, request):
        """
        Register a new lecturer.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=StudentSerializer,
        responses={status.HTTP_201_CREATED: StudentSerializer},
        summary="Register a new student.",
        description="Register a new student. Students are users who are enrolled in courses.",
    )
    @action(detail=False, methods=["POST"])
    def register_student(self, request):
        """
        Register a new student.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["users"])
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["get_all_lecturers", "get_lecturer"]:
            self.permission_classes = [IsRegistrationOfficer | IsLecturer]
        if self.action in ["get_all_classreps", "get_class_rep"]:
            self.permission_classes = [IsLecturer | IsRegistrationOfficer]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["get_all_lecturers", "get_lecturer"]:
            return LecturerSerializer
        if self.action in ["get_all_classreps", "get_class_rep"]:
            return StudentSerializer
        return super().get_serializer_class()

    @extend_schema(
        request=OpenApiTypes.NONE,
        responses={
            status.HTTP_200_OK: PolymorphicProxySerializer(
                component_name="MetaUser",
                serializers=[StudentSerializer, LecturerSerializer],
                resource_type_field_name="is_lecturer",
            ),
        },
        summary="Retrieve the current user.",
        description="Retrieve the current user.",
    )
    @action(detail=False, methods=["GET"])
    def me(self, request):
        """
        Retrieve the current user.
        """
        user = request.user
        if user.is_lecturer:
            return Response(LecturerSerializer(user).data, status=status.HTTP_200_OK)
        else:
            return Response(StudentSerializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve all lecturers.",
        description="Retrieve all lecturers. Lecturers are users who are responsible for teaching and managing courses.",
    )
    @action(detail=False, methods=["GET"])
    def get_all_lecturers(self, request):
        lecturers = self.get_queryset().filter(is_lecturer=True)
        serializer = self.get_serializer(lecturers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a lecturer.",
        description="Retrieve a lecturer. Lecturers are users who are responsible for teaching and managing courses.",
        parameters=[
            OpenApiParameter(
                name="lecturer_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            )
        ],
    )
    @action(detail=False, methods=["GET"], url_path="get_lecturer/(?P<lecturer_id>\d+)")
    def get_lecturer(self, request, lecturer_id: int = None):
        lecturers = self.get_queryset().filter(is_lecturer=True)
        lecturer = get_object_or_404(lecturers, pk=lecturer_id)
        serializer = self.get_serializer(lecturer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve all class representatives.",
        description="Retrieve all class representatives. Class representatives are students who are responsible for representing their class.",
    )
    @action(detail=False, methods=["GET"])
    def get_all_classreps(self, request):
        class_reps = self.get_queryset().filter(is_lecturer=False, is_class_rep=True)
        serializer = self.get_serializer(class_reps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a class representative.",
        description="Retrieve a class representative. Class representatives are students who are responsible for representing their class.",
        parameters=[
            OpenApiParameter(
                name="class_rep_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            )
        ],
    )
    @action(detail=False, methods=["GET"], url_path="get_student/(?P<class_rep_id>\d+)")
    def get_class_rep(self, request, class_rep_id=None):
        class_reps = self.get_queryset().filter(is_lecturer=False, is_class_rep=True)
        class_rep = get_object_or_404(class_reps, pk=class_rep_id)
        serializer = self.get_serializer(class_rep)
        return Response(serializer.data, status=status.HTTP_200_OK)
