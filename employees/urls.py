from django.urls import path

from .views import (
    EmployeeListCreateView,
    EmployeeDetailView,

    TaskListCreateView,
    TaskDetailView,

    ProjectListCreateView,
    ProjectDetailView,

    AttendanceScanView,
    TodayAttendanceView,
    MonthlyAttendanceView,

    LeaveRequestListCreateView,
    LeaveRequestDetailView,
    LeaveApprovalView,

    LeaveBalanceListCreateView,
    LeaveBalanceDetailView,

    WFHRequestListCreateView,
    WFHRequestDetailView,
    WFHApprovalView,

    NotificationListView,
    NotificationReadView,

    EmployeeDashboardView,

    ChangePasswordView,
)


urlpatterns = [

    # Employees
    path(
        '',
        EmployeeListCreateView.as_view(),
        name='employee-list'
    ),

    path(
        '<int:pk>/',
        EmployeeDetailView.as_view(),
        name='employee-detail'
    ),


    # Dashboard
    path(
        'dashboard/',
        EmployeeDashboardView.as_view(),
        name='employee-dashboard'
    ),


    # Tasks
    path(
        'tasks/',
        TaskListCreateView.as_view(),
        name='task-list'
    ),

    path(
        'tasks/<int:pk>/',
        TaskDetailView.as_view(),
        name='task-detail'
    ),


    # Projects
    path(
        'projects/',
        ProjectListCreateView.as_view(),
        name='project-list'
    ),

    path(
        'projects/<int:pk>/',
        ProjectDetailView.as_view(),
        name='project-detail'
    ),


    # Attendance
    path(
        'attendance/scan/',
        AttendanceScanView.as_view(),
        name='attendance-scan'
    ),

    path(
        'attendance/today/',
        TodayAttendanceView.as_view(),
        name='attendance-today'
    ),

    path(
        'attendance/monthly/',
        MonthlyAttendanceView.as_view(),
        name='attendance-monthly'
    ),


    # Leave
    path(
        'leave/',
        LeaveRequestListCreateView.as_view(),
        name='leave-list'
    ),

    path(
        'leave/<int:pk>/',
        LeaveRequestDetailView.as_view(),
        name='leave-detail'
    ),

    path(
        'leave/<int:pk>/approval/',
        LeaveApprovalView.as_view(),
        name='leave-approval'
    ),


    # Leave balance
    path(
        'leave-balance/',
        LeaveBalanceListCreateView.as_view(),
        name='leave-balance-list'
    ),

    path(
        'leave-balance/<int:pk>/',
        LeaveBalanceDetailView.as_view(),
        name='leave-balance-detail'
    ),


    # WFH
    path(
        'wfh/',
        WFHRequestListCreateView.as_view(),
        name='wfh-list'
    ),

    path(
        'wfh/<int:pk>/',
        WFHRequestDetailView.as_view(),
        name='wfh-detail'
    ),

    path(
        'wfh/<int:pk>/approval/',
        WFHApprovalView.as_view(),
        name='wfh-approval'
    ),


    # Notifications
    path(
        'notifications/',
        NotificationListView.as_view(),
        name='notifications'
    ),

    path(
        'notifications/<int:pk>/read/',
        NotificationReadView.as_view(),
        name='notification-read'
    ),


    # Password
    path(
        'change-password/',
        ChangePasswordView.as_view(),
        name='change-password'
    ),
]