from rest_framework import serializers
from .models import Patient, QueryLog, EpsilonBudget, User
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'organization', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientSerializer(serializers.ModelSerializer):
    bmi = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'created_at', 'updated_at']


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes"""
    class Meta:
        model = Patient
        fields = ['patient_id', 'age', 'gender', 'blood_type', 'admission_date']


class QueryLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = QueryLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class EpsilonBudgetSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    remaining_budget = serializers.ReadOnlyField()
    is_warning = serializers.ReadOnlyField()
    is_depleted = serializers.ReadOnlyField()
    
    class Meta:
        model = EpsilonBudget
        fields = ['id', 'user', 'user_username', 'total_budget', 'consumed_budget', 
                 'remaining_budget', 'is_warning', 'is_depleted', 'warning_threshold',
                 'last_reset', 'reset_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'consumed_budget', 'last_reset', 'reset_count', 
                           'created_at', 'updated_at']


# Serializers pour les requêtes

class QueryCountSerializer(serializers.Serializer):
    """Serializer pour count queries"""
    epsilon = serializers.FloatField(min_value=0.01, max_value=5.0, default=1.0)
    filters = serializers.DictField(required=False, default=dict)
    
    # Filtres possibles
    age_min = serializers.IntegerField(required=False)
    age_max = serializers.IntegerField(required=False)
    gender = serializers.ChoiceField(choices=['M', 'F', 'O'], required=False)
    blood_type = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)


class QueryMeanSerializer(serializers.Serializer):
    """Serializer pour mean queries"""
    epsilon = serializers.FloatField(min_value=0.01, max_value=5.0, default=1.0)
    columns = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'age', 'weight', 'height', 'blood_pressure_systolic',
            'blood_pressure_diastolic', 'treatment_cost'
        ]),
        min_length=1
    )
    filters = serializers.DictField(required=False, default=dict)
    
    # Bounds pour chaque colonne
    age_bounds = serializers.ListField(child=serializers.FloatField(), default=[0, 120])
    weight_bounds = serializers.ListField(child=serializers.FloatField(), default=[30, 200])
    height_bounds = serializers.ListField(child=serializers.FloatField(), default=[100, 250])
    bp_systolic_bounds = serializers.ListField(child=serializers.FloatField(), default=[50, 250])
    bp_diastolic_bounds = serializers.ListField(child=serializers.FloatField(), default=[30, 150])
    cost_bounds = serializers.ListField(child=serializers.FloatField(), default=[0, 100000])


class QuerySumSerializer(serializers.Serializer):
    """Serializer pour sum queries"""
    epsilon = serializers.FloatField(min_value=0.01, max_value=5.0, default=1.0)
    columns = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'age', 'weight', 'height', 'treatment_cost'
        ]),
        min_length=1
    )
    filters = serializers.DictField(required=False, default=dict)
    bounds = serializers.DictField(required=False, default=dict)


class QueryMedianSerializer(serializers.Serializer):
    """Serializer pour median queries"""
    epsilon = serializers.FloatField(min_value=0.01, max_value=5.0, default=1.0)
    column = serializers.ChoiceField(choices=[
        'age', 'weight', 'height', 'blood_pressure_systolic',
        'blood_pressure_diastolic', 'treatment_cost'
    ])
    filters = serializers.DictField(required=False, default=dict)
    bounds = serializers.ListField(child=serializers.FloatField(), min_length=2, max_length=2)


class QueryHistogramSerializer(serializers.Serializer):
    """Serializer pour histogram queries"""
    epsilon = serializers.FloatField(min_value=0.01, max_value=5.0, default=1.0)
    column = serializers.ChoiceField(choices=[
        'age', 'weight', 'height', 'blood_pressure_systolic',
        'blood_pressure_diastolic', 'treatment_cost'
    ])
    num_bins = serializers.IntegerField(min_value=2, max_value=50, default=10)
    filters = serializers.DictField(required=False, default=dict)
    min_value = serializers.FloatField(required=False)
    max_value = serializers.FloatField(required=False)


class DataLoadSerializer(serializers.Serializer):
    """Serializer pour charger des données"""
    patients = serializers.ListField(child=serializers.DictField())
    validate_only = serializers.BooleanField(default=False)


class EpsilonResetSerializer(serializers.Serializer):
    """Serializer pour reset epsilon budget"""
    confirm = serializers.BooleanField(default=False)
    reason = serializers.CharField(required=False, max_length=500)