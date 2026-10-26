from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Employee,
    Task,
    Project,
    AttendanceEvent,
    LeaveRequest,
    LeaveBalance,
    WFHRequest,
    Notification
)


class EmployeeSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Employee
        fields = '__all__'

        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }

    def create(self, validated_data):

        password = validated_data.pop(
            'password',
            None
        )

        employee = Employee.objects.create(
            **validated_data
        )

        if password:

            user = User.objects.create_user(
                username=employee.company_email,
                email=employee.company_email,
                password=password
            )

            employee.user = user
            employee.save()

        return employee


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class AttendanceEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceEvent
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):

    total_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id',
            'employee',
            'leave_type',
            'start_date',
            'end_date',
            'reason',
            'status',
            'created_at',
            'total_days'
        ]

    def get_total_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1

class LeaveBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveBalance
        fields = '__all__'


class WFHRequestSerializer(serializers.ModelSerializer):

    total_days = serializers.SerializerMethodField()

    class Meta:
        model = WFHRequest
        fields = [
            'id',
            'employee',
            'start_date',
            'end_date',
            'reason',
            'status',
            'created_at',
            'total_days'
        ]

    def get_total_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'