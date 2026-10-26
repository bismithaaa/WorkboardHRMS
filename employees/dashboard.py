from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Employee


class EmployeeDashboardView(APIView):
    permission_classes = []

    def get(self, request):
        employee = Employee.objects.get(user=request.user)

        return Response({
            "employee": {
                "id": employee.employee_id,
                "name": employee.full_name,
                "email": employee.company_email,
                "designation": employee.designation,
                "department": employee.department,
                "team": employee.team,
            },
            "attendance": {
                "today_hours": 0,
                "monthly_hours": 0,
                "attendance_percentage": 0
            },
            "tasks": {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0
            },
            "leave": {
                "total": 0,
                "used": 0,
                "remaining": 0
            },
            "projects": [],
            "notifications": []
        })