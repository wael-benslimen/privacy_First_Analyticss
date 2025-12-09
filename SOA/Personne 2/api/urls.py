from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet, basename='patient')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Auth
    path('auth/login/', views.login_view, name='login'),
    path('auth/me/', views.current_user, name='current-user'),
    
    # Query endpoints
    path('query/count/', views.query_count, name='query-count'),
    path('query/mean/', views.query_mean, name='query-mean'),
    path('query/sum/', views.query_sum, name='query-sum'),
    path('query/median/', views.query_median, name='query-median'),
    path('query/histogram/', views.query_histogram, name='query-histogram'),
    
    # Epsilon management
    path('epsilon/status/', views.epsilon_status, name='epsilon-status'),
    path('epsilon/reset/', views.epsilon_reset, name='epsilon-reset'),
    
    # Data management
    path('data/load/', views.data_load, name='data-load'),
    
    # Logs
    path('logs/history/', views.logs_history, name='logs-history'),
    
    # Stats
    path('stats/overview/', views.stats_overview, name='stats-overview'),
]