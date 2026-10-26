from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

from .serializers import (
    EmployeeSerializer,
    TaskSerializer,
    ProjectSerializer,
    AttendanceEventSerializer,
    LeaveRequestSerializer,
    LeaveBalanceSerializer,
    WFHRequestSerializer,
    NotificationSerializer
)

from .permissions import IsSuperAdmin


# --------------------------------------------------
# EMPLOYEE
# --------------------------------------------------

class EmployeeListCreateView(generics.ListCreateAPIView):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):

        if self.request.method == 'POST':
            return [IsSuperAdmin()]

        return []


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):

        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsSuperAdmin()]

        return []


# --------------------------------------------------
# TASK
# --------------------------------------------------

class TaskListCreateView(generics.ListCreateAPIView):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = []


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = []


# --------------------------------------------------
# PROJECT
# --------------------------------------------------

class ProjectListCreateView(generics.ListCreateAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = []


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = []


# --------------------------------------------------
# ATTENDANCE
# --------------------------------------------------

class AttendanceScanView(generics.CreateAPIView):

    queryset = AttendanceEvent.objects.all()
    serializer_class = AttendanceEventSerializer
    permission_classes = []


class TodayAttendanceView(APIView):

    permission_classes = []

    def get(self, request):

        employee_id = request.GET.get('employee')

        employee = Employee.objects.get(
            id=employee_id
        )

        events = AttendanceEvent.objects.filter(
            employee=employee,
            scanned_at__date=timezone.localdate()
        ).order_by('scanned_at')

        total_work = timedelta()

        last_in = None

        for event in events:

            if event.scan_type == 'IN':
                last_in = event.scanned_at

            elif event.scan_type == 'OUT' and last_in:

                total_work += (
                    event.scanned_at - last_in
                )

                last_in = None

        if last_in:

            total_work += (
                timezone.now() - last_in
            )

        hours = round(
            total_work.total_seconds() / 3600,
            2
        )

        return Response({
            'employee': employee.full_name,
            'date': timezone.localdate(),
            'working_hours': hours,
            'scan_count': events.count(),
            'events': AttendanceEventSerializer(
                events,
                many=True
            ).data
        })


class MonthlyAttendanceView(APIView):

    permission_classes = []

    def get(self, request):

        employee_id = request.GET.get(
            'employee'
        )

        month = int(
            request.GET.get(
                'month',
                timezone.localdate().month
            )
        )

        year = int(
            request.GET.get(
                'year',
                timezone.localdate().year
            )
        )

        events = AttendanceEvent.objects.filter(
            employee_id=employee_id,
            scanned_at__month=month,
            scanned_at__year=year
        ).order_by('scanned_at')

        return Response({
            'employee_id': employee_id,
            'month': month,
            'year': year,
            'scan_count': events.count(),
            'events': AttendanceEventSerializer(
                events,
                many=True
            ).data
        })


# --------------------------------------------------
# LEAVE
# --------------------------------------------------

class LeaveRequestListCreateView(
    generics.ListCreateAPIView
):

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = []

    def perform_create(self, serializer):

        leave = serializer.save()

        Notification.objects.create(
            employee=leave.employee,
            title='Leave Request Submitted',
            message=(
                f'Your {leave.leave_type} leave request '
                f'from {leave.start_date} to '
                f'{leave.end_date} was submitted.'
            )
        )


class LeaveRequestDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = []


class LeaveApprovalView(APIView):

    permission_classes = []

    def post(self, request, pk):

        action = request.data.get('action')

        try:
            leave = LeaveRequest.objects.get(
                id=pk
            )
        except LeaveRequest.DoesNotExist:

            return Response(
                {'error': 'Leave request not found'},
                status=404
            )

        if leave.status != 'PENDING':

            return Response(
                {'error': 'Leave already processed'},
                status=400
            )

        if action == 'REJECT':

            leave.status = 'REJECTED'
            leave.save()

            Notification.objects.create(
                employee=leave.employee,
                title='Leave Rejected',
                message='Your leave request was rejected.'
            )

            return Response(
                LeaveRequestSerializer(leave).data
            )

        if action == 'APPROVE':

            try:
                balance = LeaveBalance.objects.get(
                    employee=leave.employee
                )
            except LeaveBalance.DoesNotExist:

                return Response(
                    {'error': 'Leave balance not found'},
                    status=400
                )

            days = (
                leave.end_date -
                leave.start_date
            ).days + 1

            field_map = {
                'CASUAL': 'casual',
                'SICK': 'sick',
                'EARNED': 'earned',
                'EMERGENCY': 'emergency'
            }

            if leave.leave_type != 'UNPAID':

                field = field_map.get(
                    leave.leave_type
                )

                available = getattr(
                    balance,
                    field
                )

                if available < days:

                    return Response(
                        {
                            'error':
                            'Insufficient leave balance'
                        },
                        status=400
                    )

                setattr(
                    balance,
                    field,
                    available - days
                )

                balance.save()

            leave.status = 'APPROVED'
            leave.save()

            Notification.objects.create(
                employee=leave.employee,
                title='Leave Approved',
                message=(
                    f'Your {days}-day leave request '
                    f'has been approved.'
                )
            )

            return Response(
                LeaveRequestSerializer(leave).data
            )

        return Response(
            {
                'error':
                'action must be APPROVE or REJECT'
            },
            status=400
        )


# --------------------------------------------------
# LEAVE BALANCE
# --------------------------------------------------

class LeaveBalanceListCreateView(
    generics.ListCreateAPIView
):

    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = []


class LeaveBalanceDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = []


# --------------------------------------------------
# WFH
# --------------------------------------------------

class WFHRequestListCreateView(
    generics.ListCreateAPIView
):

    queryset = WFHRequest.objects.all()
    serializer_class = WFHRequestSerializer
    permission_classes = []

    def perform_create(self, serializer):

        wfh = serializer.save()

        Notification.objects.create(
            employee=wfh.employee,
            title='WFH Request Submitted',
            message=(
                f'Your WFH request from '
                f'{wfh.start_date} to '
                f'{wfh.end_date} was submitted.'
            )
        )


class WFHRequestDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = WFHRequest.objects.all()
    serializer_class = WFHRequestSerializer
    permission_classes = []


class WFHApprovalView(APIView):

    permission_classes = []

    def post(self, request, pk):

        action = request.data.get('action')

        try:
            wfh = WFHRequest.objects.get(
                id=pk
            )
        except WFHRequest.DoesNotExist:

            return Response(
                {'error': 'WFH request not found'},
                status=404
            )

        if action == 'APPROVE':

            wfh.status = 'APPROVED'
            wfh.save()

            Notification.objects.create(
                employee=wfh.employee,
                title='WFH Approved',
                message='Your WFH request was approved.'
            )

        elif action == 'REJECT':

            wfh.status = 'REJECTED'
            wfh.save()

            Notification.objects.create(
                employee=wfh.employee,
                title='WFH Rejected',
                message='Your WFH request was rejected.'
            )

        else:

            return Response(
                {
                    'error':
                    'action must be APPROVE or REJECT'
                },
                status=400
            )

        return Response(
            WFHRequestSerializer(wfh).data
        )


# --------------------------------------------------
# NOTIFICATIONS
# --------------------------------------------------

class NotificationListView(
    generics.ListAPIView
):

    serializer_class = NotificationSerializer
    permission_classes = []

    def get_queryset(self):

        employee_id = self.request.GET.get(
            'employee'
        )

        return Notification.objects.filter(
            employee_id=employee_id
        ).order_by('-created_at')


class NotificationReadView(APIView):

    permission_classes = []

    def post(self, request, pk):

        try:
            notification = Notification.objects.get(
                id=pk
            )
        except Notification.DoesNotExist:

            return Response(
                {'error': 'Notification not found'},
                status=404
            )

        notification.is_read = True
        notification.save()

        return Response(
            NotificationSerializer(
                notification
            ).data
        )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

class EmployeeDashboardView(APIView):

    permission_classes = []

    def get(self, request):

        employee_id = request.GET.get(
            'employee'
        )

        try:
            employee = Employee.objects.get(
                id=employee_id
            )
        except Employee.DoesNotExist:

            return Response(
                {'error': 'Employee not found'},
                status=404
            )

        tasks = Task.objects.filter(
            assigned_to=employee
        )

        projects = Project.objects.filter(
            assigned_employees=employee
        )

        leaves = LeaveRequest.objects.filter(
            employee=employee
        )

        approved_leaves = leaves.filter(
            status='APPROVED'
        )

        try:
            balance = LeaveBalance.objects.get(
                employee=employee
            )

            leave_balance = {
                'casual': balance.casual,
                'sick': balance.sick,
                'earned': balance.earned,
                'emergency': balance.emergency
            }

        except LeaveBalance.DoesNotExist:

            leave_balance = {}

        notifications = Notification.objects.filter(
            employee=employee
        ).order_by('-created_at')[:10]

        return Response({

            'employee': {
                'id': employee.employee_id,
                'name': employee.full_name,
                'email': employee.company_email,
                'designation': employee.designation,
                'department': employee.department,
                'team': employee.team,
                'role': employee.role
            },

            'tasks': {
                'total': tasks.count(),

                'pending': tasks.filter(
                    status='PENDING'
                ).count(),

                'in_progress': tasks.filter(
                    status='IN_PROGRESS'
                ).count(),

                'completed': tasks.filter(
                    status='COMPLETED'
                ).count()
            },

            'projects': ProjectSerializer(
                projects,
                many=True
            ).data,

            'leave': {
                'total_requests': leaves.count(),
                'approved': approved_leaves.count(),
                'pending': leaves.filter(
                    status='PENDING'
                ).count(),
                'balance': leave_balance
            },

            'notifications': NotificationSerializer(
                notifications,
                many=True
            ).data
        })


# --------------------------------------------------
# PASSWORD
# --------------------------------------------------

class ChangePasswordView(APIView):

    permission_classes = []

    def post(self, request):

        employee_id = request.data.get(
            'employee'
        )

        old_password = request.data.get(
            'old_password'
        )

        new_password = request.data.get(
            'new_password'
        )

        try:
            employee = Employee.objects.get(
                id=employee_id
            )
        except Employee.DoesNotExist:

            return Response(
                {'error': 'Employee not found'},
                status=404
            )

        if not employee.user:

            return Response(
                {'error': 'Employee has no login account'},
                status=400
            )

        user = employee.user

        if not user.check_password(
            old_password
        ):

            return Response(
                {'error': 'Old password is incorrect'},
                status=400
            )

        if not new_password or len(new_password) < 8:

            return Response(
                {
                    'error':
                    'New password must be at least 8 characters'
                },
                status=400
            )

        user.set_password(new_password)
        user.save()

        return Response({
            'message':
            'Password changed successfully'
        })