from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class User(AbstractUser):
    """Utilisateur personnalisé"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('analyst', 'Data Analyst'),
        ('researcher', 'Researcher'),
        ('viewer', 'Viewer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='analyst')
    organization = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} - {self.role}"


class Patient(models.Model):
    """Données patients avec 10 champs détaillés"""
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_TYPES = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
                   ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')]
    
    patient_id = models.CharField(max_length=50, unique=True, db_index=True, 
                                  default=uuid.uuid4, editable=False)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    zip_code = models.CharField(max_length=10)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    weight = models.FloatField(validators=[MinValueValidator(1)])
    height = models.FloatField(validators=[MinValueValidator(1)])
    blood_pressure_systolic = models.IntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    blood_pressure_diastolic = models.IntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(150)]
    )
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2)
    diagnosis = models.TextField()
    admission_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-admission_date']
        indexes = [
            models.Index(fields=['age']),
            models.Index(fields=['gender']),
            models.Index(fields=['zip_code']),
            models.Index(fields=['admission_date']),
        ]
    
    def __str__(self):
        return f"Patient {self.patient_id}"
    
    @property
    def bmi(self):
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)


class EpsilonBudget(models.Model):
    """Budget epsilon par utilisateur avec tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='epsilon_budget')
    total_budget = models.FloatField(default=10.0)
    consumed_budget = models.FloatField(default=0.0)
    warning_threshold = models.FloatField(default=2.0)
    last_reset = models.DateTimeField(default=timezone.now)
    reset_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'epsilon_budgets'
    
    @property
    def remaining_budget(self):
        return round(self.total_budget - self.consumed_budget, 4)
    
    @property
    def is_warning(self):
        return self.remaining_budget <= self.warning_threshold
    
    @property
    def is_depleted(self):
        return self.remaining_budget <= 0
    
    def can_consume(self, epsilon):
        return self.remaining_budget >= epsilon
    
    def consume(self, epsilon):
        if self.can_consume(epsilon):
            self.consumed_budget += epsilon
            self.save()
            return True
        return False
    
    def reset(self):
        self.consumed_budget = 0.0
        self.last_reset = timezone.now()
        self.reset_count += 1
        self.save()
    
    def __str__(self):
        return f"{self.user.username}: {self.remaining_budget}/{self.total_budget}"


class QueryLog(models.Model):
    """Log détaillé avec timestamps"""
    QUERY_TYPES = [
        ('count', 'Count'),
        ('mean', 'Mean'),
        ('sum', 'Sum'),
        ('median', 'Median'),
        ('histogram', 'Histogram'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked - Insufficient Budget'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='query_logs')
    query_type = models.CharField(max_length=20, choices=QUERY_TYPES)
    epsilon_used = models.FloatField()
    delta_used = models.FloatField(default=0.0)
    noise_scale = models.FloatField(null=True, blank=True)
    query_params = models.JSONField(default=dict)
    filters_applied = models.JSONField(default=dict)
    result_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    execution_time = models.FloatField(help_text="Execution time in seconds")
    rows_affected = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'query_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['query_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.query_type} - {self.status}"