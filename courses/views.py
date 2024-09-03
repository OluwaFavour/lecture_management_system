from typing import Any
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiParameter,
    extend_schema_view,
)

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Course, DayOfWeek, SpecialCourse, Tag, Level
from authentication.permissions import (
    IsLecturer,
    IsStudent,
    IsAdmin,
    IsRegistrationOfficer,
)
from authentication.models import User
from .serializers import (
    CourseCreateSerializer,
    CourseSerializer,
    AssistantUpdateSerializer,
    CourseForTheWeekSerializer,
    DayCourses,
    SpecialCourseSerializer,
)


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        summary="Lists all courses in the database",
        description="Lists all courses in the database. This action can only be performed by a lecturer or an admin",
    ),
    retrieve=extend_schema(
        summary="Retrieve a course by its ID",
        description="Retrieve a course by its ID. This action can only be performed by a lecturer or an admin",
    ),
    create=extend_schema(
        summary="Create a course",
        description="Create a course. This action can only be performed by a lecturer or an admin",
    ),
    update=extend_schema(
        summary="Update a course",
        description="Update a course. This action can only be performed by a lecturer or an admin",
    ),
    partial_update=extend_schema(
        summary="Partially update a course",
        description="Partially update a course. This action can only be performed by a lecturer or an admin",
    ),
    destroy=extend_schema(
        summary="Delete a course",
        description="Delete a course. This action can only be performed by a lecturer or an admin",
    ),
)
@extend_schema(tags=["courses"])
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "add_assistant",
            "remove_assistant",
        ]:
            return [IsLecturer(), IsAdmin(), IsRegistrationOfficer()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsRegistrationOfficer(), IsAdmin()]
        if self.action in ["get_my_courses_for_the_week", "tag"]:
            return [IsStudent()]
        if self.action == "get_courses_by_level":
            return [IsLecturer(), IsAdmin(), IsStudent()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CourseCreateSerializer
        if self.action in ["add_assistant", "remove_assistant"]:
            return AssistantUpdateSerializer
        if self.action == "get_my_courses_for_the_week":
            return CourseForTheWeekSerializer
        if self.action == "tag":
            return SpecialCourseSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=AssistantUpdateSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                "AssistantUpdate200", {"message": serializers.CharField()}
            ),
            status.HTTP_404_NOT_FOUND: inline_serializer(
                "AssistantUpdate404", {"error": serializers.CharField()}
            ),
        },
        summary="Add an assistant to a course",
        description="Add an assistant to a course. Can only be done by a lecturer or admin.",
    )
    @action(detail=True, methods=["POST"])
    def add_assistant(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assistant_pk = serializer.validated_data["assistant"]
        try:
            assistant = User.objects.get(pk=assistant_pk)
            course: Course = self.get_object()
            course.assistants.add(assistant)
        except User.DoesNotExist:
            return Response(
                {"error": "Assistant does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"message": "Assistant added successfully"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        request=AssistantUpdateSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                "AssistantDelete200", {"message": serializers.CharField()}
            ),
            status.HTTP_404_NOT_FOUND: inline_serializer(
                "AssistantDelete404", {"error": serializers.CharField()}
            ),
        },
        summary="Remove an assistant from a course",
        description="Remove an assistant from a course. Can only be done by a lecturer or admin.",
    )
    @action(detail=True, methods=["DELETE"])
    def remove_assistant(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assistant_pk = serializer.validated_data["assistant"]
        try:
            assistant = User.objects.get(pk=assistant_pk)
            course: Course = self.get_object()
            course.assistants.remove(assistant)
        except User.DoesNotExist:
            return Response(
                {"error": "Assistant does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"message": "Assistant removed successfully"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        description="Get the courses for the current week",
        summary="Get courses for the week for the logged in student",
    )
    @action(detail=False, methods=["GET"])
    def get_my_courses_for_the_week(self, request):
        """
        Get the courses for the current week.
        """
        user: User = request.user
        student_level: int = user.level

        # Student courses are all courses with the same level as the student
        courses = Course.objects.filter(level=student_level)
        data = [
            DayCourses(day=day, courses=courses.filter(day=day[0]))
            for day in DayOfWeek.choices
        ]
        serializer = CourseForTheWeekSerializer(data, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Tag a course as special - carry over or spill over",
        parameters=[
            OpenApiParameter(
                name="tag",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="The tag to mark the course as, either 'CO' for Carry Over or 'SO' for Spill Over",
                enum=Tag.__members__.values(),
            )
        ],
        request=OpenApiTypes.NONE,
        summary="Tag a course as special - carry over or spill over. Client can decide to display spill over courses or remove carry over courses in students courses and schedule",
    )
    @action(detail=True, methods=["POST"])
    def tag(self, request, pk=None):
        tag = request.query_params.get("tag")
        if not tag:
            return Response(
                {"error": "The tag query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if tag not in Tag.__members__.values():
            return Response(
                {"error": "Invalid tag value"}, status=status.HTTP_400_BAD_REQUEST
            )

        course: Course = self.get_object()
        student: User = request.user

        # Check if the course is already tagged as special for the student
        if SpecialCourse.objects.filter(base_course=course, students=student).exists():
            return Response(
                {"error": "Course already tagged"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Use get_or_create to handle the creation or retrieval in one step
        special_course, created = SpecialCourse.objects.get_or_create(
            base_course=course, tag=tag
        )
        if created or not special_course.students.filter(pk=student.pk).exists():
            special_course.students.add(student)

        serializer = SpecialCourseSerializer(special_course)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Get courses by level",
        summary="Get courses by level. The client can use this to get all courses done by a student using their level",
        parameters=[
            OpenApiParameter(
                name="level",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="The level of the courses to get, either 100, 200, 300, 400 or 500",
                enum=Level.__members__.values(),
            )
        ],
        responses=CourseSerializer(many=True),
    )
    @action(detail=False, methods=["GET"])
    def get_courses_by_level(self, level):
        query_params: dict[str, Any] = self.request.query_params
        level = query_params.get("level")
        if not level:
            return Response(
                {"error": "The level query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if level not in Level.__members__.values():
            return Response(
                {"error": "Invalid level value"}, status=status.HTTP_400_BAD_REQUEST
            )

        courses = Course.objects.filter(level=level)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
