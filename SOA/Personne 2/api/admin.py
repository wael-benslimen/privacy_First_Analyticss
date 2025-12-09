from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Patient, EpsilonBudget, QueryLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'organization']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'organization')}),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'age', 'gender', 'blood_type', 'treatment_cost', 
                    'admission_date', 'created_at']
    list_filter = ['gender', 'blood_type', 'admission_date']
    search_fields = ['patient_id', 'zip_code', 'diagnosis']
    date_hierarchy = 'admission_date'
    ordering = ['-admission_date']
    
    readonly_fields = ['patient_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('patient_id',)
        }),
        ('Demographics', {
            'fields': ('age', 'gender', 'zip_code')
        }),
        ('Medical Info', {
            'fields': ('blood_type', 'weight', 'height', 
                      'blood_pressure_systolic', 'blood_pressure_diastolic')
        }),
        ('Treatment', {
            'fields': ('diagnosis', 'treatment_cost', 'admission_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EpsilonBudget)
class EpsilonBudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'remaining_budget_display', 'total_budget', 
                    'is_warning', 'last_reset', 'reset_count']
    list_filter = ['last_reset']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at', 'remaining_budget_display']
    
    def remaining_budget_display(self, obj):
        return f"{obj.remaining_budget}/{obj.total_budget}"
    remaining_budget_display.short_description = 'Remaining/Total'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Budget', {
            'fields': ('total_budget', 'consumed_budget', 'remaining_budget_display', 
                      'warning_threshold')
        }),
        ('History', {
            'fields': ('last_reset', 'reset_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'query_type', 'epsilon_used', 'status', 
                    'execution_time', 'timestamp']
    list_filter = ['query_type', 'status', 'timestamp']
    search_fields = ['user__username', 'id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['id', 'timestamp', 'execution_time']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Query Info', {
            'fields': ('id', 'user', 'query_type', 'timestamp')
        }),
        ('Privacy Parameters', {
            'fields': ('epsilon_used', 'delta_used', 'noise_scale')
        }),
        ('Details', {
            'fields': ('query_params', 'filters_applied', 'result_data')
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'execution_time', 'rows_affected')
        }),
        ('Audit', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
