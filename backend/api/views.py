from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import time
import numpy as np

from .models import Patient, QueryLog, EpsilonBudget
from .serializers import (
    PatientSerializer, PatientListSerializer, QueryLogSerializer,
    EpsilonBudgetSerializer, UserSerializer,
    QueryCountSerializer, QueryMeanSerializer, QuerySumSerializer,
    QueryMedianSerializer, QueryHistogramSerializer,
    DataLoadSerializer, EpsilonResetSerializer
)
from .services import DifferentialPrivacyService, PolicyEnforcer

User = get_user_model()


def get_client_ip(request):
    """Obtenir l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_query(user, query_type, epsilon, delta, query_params, result_data, 
              status_type, error_msg, exec_time, rows, request):
    """Créer un log de requête"""
    QueryLog.objects.create(
        user=user,
        query_type=query_type,
        epsilon_used=epsilon,
        delta_used=delta,
        query_params=query_params,
        result_data=result_data,
        status=status_type,
        error_message=error_msg,
        execution_time=exec_time,
        rows_affected=rows,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )


def apply_filters(queryset, filters):
    """Appliquer les filtres au queryset"""
    if 'age_min' in filters:
        queryset = queryset.filter(age__gte=filters['age_min'])
    if 'age_max' in filters:
        queryset = queryset.filter(age__lte=filters['age_max'])
    if 'gender' in filters:
        queryset = queryset.filter(gender=filters['gender'])
    if 'blood_type' in filters:
        queryset = queryset.filter(blood_type=filters['blood_type'])
    if 'zip_code' in filters:
        queryset = queryset.filter(zip_code=filters['zip_code'])
    
    return queryset


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet pour les patients"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    def list(self, request, *args, **kwargs):
        """Liste des patients (limitée pour privacy)"""
        # Limiter à 10 patients pour la démo
        queryset = self.filter_queryset(self.get_queryset())[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'note': 'Only showing first 10 patients for privacy',
            'results': serializer.data
        })


@swagger_auto_schema(
    method='post',
    request_body=QueryCountSerializer,
    responses={200: openapi.Response('Success', openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'query_type': openapi.Schema(type=openapi.TYPE_STRING),
            'result': openapi.Schema(type=openapi.TYPE_OBJECT),
            'epsilon_used': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ))}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_count(request):
    """Count query avec DP"""
    start_time = time.time()
    
    serializer = QueryCountSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    epsilon = data.get('epsilon', 1.0)
    filters = data.get('filters', {})
    
    # Récupérer epsilon budget
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    enforcer = PolicyEnforcer(request.user, epsilon_budget)
    
    # Vérifier autorisation
    can_execute, message = enforcer.can_execute_query(epsilon)
    if not can_execute:
        exec_time = time.time() - start_time
        log_query(request.user, 'count', epsilon, 0, data, None, 
                 'blocked', message, exec_time, 0, request)
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Exécuter requête
        queryset = Patient.objects.all()
        queryset = apply_filters(queryset, filters)
        true_count = queryset.count()
        
        # Appliquer DP
        dp_service = DifferentialPrivacyService(epsilon=epsilon)
        result = dp_service.noisy_count(true_count)
        
        # Consommer budget
        enforcer.consume_budget(epsilon)
        
        exec_time = time.time() - start_time
        
        # Log
        log_query(request.user, 'count', epsilon, 0, data, result,
                 'success', '', exec_time, true_count, request)
        
        return Response({
            'query_type': 'count',
            'result': result,
            'epsilon_used': epsilon,
            'filters_applied': filters,
            'execution_time': round(exec_time, 4),
            'budget_remaining': epsilon_budget.remaining_budget
        })
        
    except Exception as e:
        exec_time = time.time() - start_time
        log_query(request.user, 'count', epsilon, 0, data, None,
                 'error', str(e), exec_time, 0, request)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=QueryMeanSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_mean(request):
    """Mean query avec DP pour multi-colonnes"""
    start_time = time.time()
    
    serializer = QueryMeanSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    epsilon = data.get('epsilon', 1.0)
    columns = data['columns']
    filters = data.get('filters', {})
    
    # Budget management
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    enforcer = PolicyEnforcer(request.user, epsilon_budget)
    
    # Epsilon par colonne
    epsilon_per_column = epsilon / len(columns)
    
    can_execute, message = enforcer.can_execute_query(epsilon)
    if not can_execute:
        exec_time = time.time() - start_time
        log_query(request.user, 'mean', epsilon, 0, data, None,
                 'blocked', message, exec_time, 0, request)
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        queryset = Patient.objects.all()
        queryset = apply_filters(queryset, filters)
        count = queryset.count()
        
        if count == 0:
            return Response({'error': 'No data matching filters'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        results = {}
        bounds_map = {
            'age': data.get('age_bounds', [0, 120]),
            'weight': data.get('weight_bounds', [30, 200]),
            'height': data.get('height_bounds', [100, 250]),
            'blood_pressure_systolic': data.get('bp_systolic_bounds', [50, 250]),
            'blood_pressure_diastolic': data.get('bp_diastolic_bounds', [30, 150]),
            'treatment_cost': data.get('cost_bounds', [0, 100000]),
        }
        
        for column in columns:
            true_mean = queryset.aggregate(avg=Avg(column))['avg']
            if true_mean is not None:
                bounds = tuple(bounds_map.get(column, [0, 1000]))
                dp_service = DifferentialPrivacyService(epsilon=epsilon_per_column)
                result = dp_service.noisy_mean(float(true_mean), bounds, count)
                results[column] = result
        
        enforcer.consume_budget(epsilon)
        exec_time = time.time() - start_time
        
        log_query(request.user, 'mean', epsilon, 0, data, results,
                 'success', '', exec_time, count, request)
        
        return Response({
            'query_type': 'mean',
            'results': results,
            'epsilon_used': epsilon,
            'epsilon_per_column': epsilon_per_column,
            'columns': columns,
            'filters_applied': filters,
            'execution_time': round(exec_time, 4),
            'budget_remaining': epsilon_budget.remaining_budget
        })
        
    except Exception as e:
        exec_time = time.time() - start_time
        log_query(request.user, 'mean', epsilon, 0, data, None,
                 'error', str(e), exec_time, 0, request)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=QuerySumSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_sum(request):
    """Sum query avec DP et agrégations"""
    start_time = time.time()
    
    serializer = QuerySumSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    epsilon = data.get('epsilon', 1.0)
    columns = data['columns']
    filters = data.get('filters', {})
    
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    enforcer = PolicyEnforcer(request.user, epsilon_budget)
    
    epsilon_per_column = epsilon / len(columns)
    
    can_execute, message = enforcer.can_execute_query(epsilon)
    if not can_execute:
        exec_time = time.time() - start_time
        log_query(request.user, 'sum', epsilon, 0, data, None,
                 'blocked', message, exec_time, 0, request)
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        queryset = Patient.objects.all()
        queryset = apply_filters(queryset, filters)
        count = queryset.count()
        
        if count == 0:
            return Response({'error': 'No data matching filters'},
                          status=status.HTTP_404_NOT_FOUND)
        
        results = {}
        default_bounds = {
            'age': (0, 120),
            'weight': (30, 200),
            'height': (100, 250),
            'treatment_cost': (0, 100000),
        }
        
        for column in columns:
            true_sum = queryset.aggregate(total=Sum(column))['total']
            if true_sum is not None:
                bounds = data.get('bounds', {}).get(column, default_bounds.get(column, (0, 1000)))
                dp_service = DifferentialPrivacyService(epsilon=epsilon_per_column)
                result = dp_service.noisy_sum(float(true_sum), bounds, count)
                results[column] = result
        
        enforcer.consume_budget(epsilon)
        exec_time = time.time() - start_time
        
        log_query(request.user, 'sum', epsilon, 0, data, results,
                 'success', '', exec_time, count, request)
        
        return Response({
            'query_type': 'sum',
            'results': results,
            'epsilon_used': epsilon,
            'filters_applied': filters,
            'execution_time': round(exec_time, 4),
            'budget_remaining': epsilon_budget.remaining_budget
        })
        
    except Exception as e:
        exec_time = time.time() - start_time
        log_query(request.user, 'sum', epsilon, 0, data, None,
                 'error', str(e), exec_time, 0, request)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# **Continue dans la prochaine partie avec median, histogram et autres endpoints...**
@swagger_auto_schema(
    method='post',
    request_body=QueryMedianSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_median(request):
    """Median query avec DP"""
    start_time = time.time()
    
    serializer = QueryMedianSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    epsilon = data.get('epsilon', 1.0)
    column = data['column']
    filters = data.get('filters', {})
    bounds = tuple(data['bounds'])
    
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    enforcer = PolicyEnforcer(request.user, epsilon_budget)
    
    can_execute, message = enforcer.can_execute_query(epsilon)
    if not can_execute:
        exec_time = time.time() - start_time
        log_query(request.user, 'median', epsilon, 0, data, None,
                 'blocked', message, exec_time, 0, request)
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        queryset = Patient.objects.all()
        queryset = apply_filters(queryset, filters)
        
        # Récupérer toutes les valeurs
        values = list(queryset.values_list(column, flat=True))
        
        if not values:
            return Response({'error': 'No data matching filters'},
                          status=status.HTTP_404_NOT_FOUND)
        
        # Convertir en float
        values = [float(v) for v in values if v is not None]
        
        dp_service = DifferentialPrivacyService(epsilon=epsilon)
        result = dp_service.noisy_median(values, bounds)
        
        enforcer.consume_budget(epsilon)
        exec_time = time.time() - start_time
        
        log_query(request.user, 'median', epsilon, 0, data, result,
                 'success', '', exec_time, len(values), request)
        
        return Response({
            'query_type': 'median',
            'column': column,
            'result': result,
            'epsilon_used': epsilon,
            'filters_applied': filters,
            'execution_time': round(exec_time, 4),
            'budget_remaining': epsilon_budget.remaining_budget
        })
        
    except Exception as e:
        exec_time = time.time() - start_time
        log_query(request.user, 'median', epsilon, 0, data, None,
                 'error', str(e), exec_time, 0, request)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=QueryHistogramSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_histogram(request):
    """Histogram query avec DP"""
    start_time = time.time()
    
    serializer = QueryHistogramSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    epsilon = data.get('epsilon', 1.0)
    column = data['column']
    num_bins = data.get('num_bins', 10)
    filters = data.get('filters', {})
    
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    enforcer = PolicyEnforcer(request.user, epsilon_budget)
    
    can_execute, message = enforcer.can_execute_query(epsilon)
    if not can_execute:
        exec_time = time.time() - start_time
        log_query(request.user, 'histogram', epsilon, 0, data, None,
                 'blocked', message, exec_time, 0, request)
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        queryset = Patient.objects.all()
        queryset = apply_filters(queryset, filters)
        
        # Récupérer valeurs
        values = list(queryset.values_list(column, flat=True))
        values = [float(v) for v in values if v is not None]
        
        if not values:
            return Response({'error': 'No data matching filters'},
                          status=status.HTTP_404_NOT_FOUND)
        
        # Déterminer min/max
        min_val = data.get('min_value', min(values))
        max_val = data.get('max_value', max(values))
        
        # Créer bins
        bin_edges = np.linspace(min_val, max_val, num_bins + 1)
        hist, _ = np.histogram(values, bins=bin_edges)
        
        # Appliquer DP
        dp_service = DifferentialPrivacyService(epsilon=epsilon)
        result = dp_service.noisy_histogram(hist.tolist(), num_bins)
        
        enforcer.consume_budget(epsilon)
        exec_time = time.time() - start_time
        
        # Formater pour réponse
        result['bin_edges'] = bin_edges.tolist()
        result['bin_labels'] = [
            f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" 
            for i in range(num_bins)
        ]
        
        log_query(request.user, 'histogram', epsilon, 0, data, result,
                 'success', '', exec_time, len(values), request)
        
        return Response({
            'query_type': 'histogram',
            'column': column,
            'result': result,
            'epsilon_used': epsilon,
            'filters_applied': filters,
            'execution_time': round(exec_time, 4),
            'budget_remaining': epsilon_budget.remaining_budget
        })
        
    except Exception as e:
        exec_time = time.time() - start_time
        log_query(request.user, 'histogram', epsilon, 0, data, None,
                 'error', str(e), exec_time, 0, request)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def epsilon_status(request):
    """GET /api/epsilon/status - Statut du budget epsilon"""
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    enforcer = PolicyEnforcer(request.user, epsilon_budget)
    
    status_data = enforcer.get_status()
    
    return Response(status_data)


@swagger_auto_schema(
    method='post',
    request_body=EpsilonResetSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def epsilon_reset(request):
    """POST /api/epsilon/reset - Reset budget epsilon"""
    serializer = EpsilonResetSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    if not data.get('confirm', False):
        return Response({
            'error': 'Confirmation required. Set confirm=true'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    
    old_consumed = epsilon_budget.consumed_budget
    epsilon_budget.reset()
    
    return Response({
        'message': 'Epsilon budget reset successfully',
        'previous_consumed': old_consumed,
        'new_remaining': epsilon_budget.remaining_budget,
        'reset_count': epsilon_budget.reset_count,
        'reason': data.get('reason', 'No reason provided')
    })


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'confirm': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def platform_reset(request):
    """POST /api/platform/reset - Reset complet de la plateforme (logs + budget)"""
    confirm = request.data.get('confirm', False)
    
    if not confirm:
        return Response({
            'error': 'Confirmation required. Set confirm=true'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    # 1. Reset Budget
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    epsilon_budget.reset()
    
    # 2. Clear Logs (For the current user or all if admin? Let's say all for "Platform Reset")
    if request.user.role == 'admin':
        deleted_count, _ = QueryLog.objects.all().delete()
    else:
        # Default fallback: clear own logs
        deleted_count, _ = QueryLog.objects.filter(user=request.user).delete()
    
    return Response({
        'message': 'Platform reset successfully',
        'logs_deleted': deleted_count,
        'budget_reset': True
    })


@swagger_auto_schema(
    method='post',
    request_body=DataLoadSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def data_load(request):
    """POST /api/data/load - Charger des données avec validation"""
    
    # Vérifier que l'utilisateur est admin
    if request.user.role != 'admin':
        return Response({
            'error': 'Only administrators can load data'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DataLoadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    patients_data = data['patients']
    validate_only = data.get('validate_only', False)
    
    errors = []
    valid_patients = []
    
    # Valider chaque patient
    for idx, patient_data in enumerate(patients_data):
        patient_serializer = PatientSerializer(data=patient_data)
        if patient_serializer.is_valid():
            valid_patients.append(patient_serializer)
        else:
            errors.append({
                'index': idx,
                'errors': patient_serializer.errors
            })
    
    if validate_only:
        return Response({
            'valid_count': len(valid_patients),
            'error_count': len(errors),
            'errors': errors[:10]  # Limiter à 10 erreurs
        })
    
    # Sauvegarder si pas d'erreurs
    if not errors:
        created_patients = []
        for patient_serializer in valid_patients:
            patient = patient_serializer.save()
            created_patients.append(patient.patient_id)
        
        return Response({
            'message': 'Data loaded successfully',
            'created_count': len(created_patients),
            'patient_ids': created_patients[:20]  # Limiter à 20 IDs
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'error': 'Validation failed',
            'valid_count': len(valid_patients),
            'error_count': len(errors),
            'errors': errors[:10]
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logs_history(request):
    """GET /api/logs/history - Historique des requêtes avec pagination"""
    
    # Filtres optionnels
    query_type = request.query_params.get('query_type')
    status_filter = request.query_params.get('status')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    # Base queryset
    if request.user.role == 'admin':
        # Admin voit tous les logs
        queryset = QueryLog.objects.all()
    else:
        # Utilisateurs voient seulement leurs logs
        queryset = QueryLog.objects.filter(user=request.user)
    
    # Appliquer filtres
    if query_type:
        queryset = queryset.filter(query_type=query_type)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if date_from:
        queryset = queryset.filter(timestamp__gte=date_from)
    if date_to:
        queryset = queryset.filter(timestamp__lte=date_to)
    
    # Pagination
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 20
    
    page = paginator.paginate_queryset(queryset, request)
    serializer = QueryLogSerializer(page, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_overview(request):
    """GET /api/stats/overview - Vue d'ensemble des statistiques"""
    
    # Stats pour l'utilisateur courant
    user_logs = QueryLog.objects.filter(user=request.user)
    
    # Compter par type
    query_type_counts = user_logs.values('query_type').annotate(
        count=Count('id')
    )
    
    # Compter par statut
    status_counts = user_logs.values('status').annotate(
        count=Count('id')
    )
    
    # Total epsilon consommé
    total_epsilon = sum(log.epsilon_used for log in user_logs)
    
    # Budget actuel
    epsilon_budget, _ = EpsilonBudget.objects.get_or_create(user=request.user)
    
    # Stats patients (si admin)
    patient_stats = {}
    if request.user.role == 'admin':
        patient_stats = {
            'total_patients': Patient.objects.count(),
            'gender_distribution': Patient.objects.values('gender').annotate(
                count=Count('id')
            ),
            'avg_age': Patient.objects.aggregate(Avg('age'))['age__avg'],
        }
    
    return Response({
        'user': {
            'username': request.user.username,
            'role': request.user.role,
        },
        'query_statistics': {
            'total_queries': user_logs.count(),
            'by_type': list(query_type_counts),
            'by_status': list(status_counts),
            'total_epsilon_consumed': round(total_epsilon, 4),
        },
        'epsilon_budget': {
            'total': epsilon_budget.total_budget,
            'consumed': epsilon_budget.consumed_budget,
            'remaining': epsilon_budget.remaining_budget,
            'is_warning': epsilon_budget.is_warning,
        },
        'patient_statistics': patient_stats,
        'last_query': QueryLogSerializer(
            user_logs.first()
        ).data if user_logs.exists() else None
    })


# Vue pour JWT login
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login et obtenir JWT tokens"""
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'User account is disabled'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Créer JWT tokens
    refresh = RefreshToken.for_user(user)
    
    # Assurer que epsilon budget existe
    EpsilonBudget.objects.get_or_create(user=user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Obtenir l'utilisateur courant"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
