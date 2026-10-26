from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):

    ROLE_CHOICES = [
        ('ADMIN', 'Super Admin'),
        ('TEAM_LEAD', 'Team Lead'),
        ('EMPLOYEE', 'Employee'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='EMPLOYEE'
    )

    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_employees'
    )

    team_lead = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )

    team = models.CharField(
        max_length=100,
        blank=True
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True
    )

    full_name = models.CharField(
        max_length=100
    )

    company_email = models.EmailField(
        unique=True
    )

    personal_email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    designation = models.CharField(
        max_length=100
    )

    department = models.CharField(
        max_length=100
    )

    date_of_joining = models.DateField()

    employment_status = models.CharField(
        max_length=20,
        default='Active'
    )

    # Profile information

    photo = models.ImageField(
        upload_to='employee_photos/',
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=20,
        blank=True
    )

    current_address = models.TextField(
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True
    )

    skills = models.TextField(
        blank=True
    )

    education = models.TextField(
        blank=True
    )

    previous_experience = models.TextField(
        blank=True
    )

    pan_number = models.CharField(
        max_length=20,
        blank=True
    )

    aadhaar_number = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.full_name


class Task(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    task_number = models.CharField(
        max_length=20,
        unique=True
    )

    title = models.CharField(
        max_length=200
    )

    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )

    deadline = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    comments = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.task_number} - {self.title}"


class Project(models.Model):

    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
    ]

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    start_date = models.DateField()

    deadline = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UPCOMING'
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    assigned_employees = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='projects'
    )

    def __str__(self):
        return self.name


class AttendanceEvent(models.Model):

    SCAN_TYPES = [
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_events'
    )

    scan_type = models.CharField(
        max_length=3,
        choices=SCAN_TYPES
    )

    scanned_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.full_name} - {self.scan_type}"


class LeaveRequest(models.Model):

    LEAVE_TYPES = [
        ('CASUAL', 'Casual'),
        ('SICK', 'Sick'),
        ('EARNED', 'Earned'),
        ('EMERGENCY', 'Emergency'),
        ('UNPAID', 'Unpaid'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPES
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type}"


class LeaveBalance(models.Model):

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balance'
    )

    casual = models.PositiveIntegerField(
        default=12
    )

    sick = models.PositiveIntegerField(
        default=10
    )

    earned = models.PositiveIntegerField(
        default=15
    )

    emergency = models.PositiveIntegerField(
        default=5
    )

    def __str__(self):
        return f"{self.employee.full_name} - Leave Balance"


class WFHRequest(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='wfh_requests'
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee.full_name} - WFH"


class Notification(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title