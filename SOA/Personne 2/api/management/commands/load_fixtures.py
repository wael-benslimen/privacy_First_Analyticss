from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Patient, EpsilonBudget
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Load 100 test patients and setup users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')
        
        # Créer utilisateurs de test
        self.create_users()
        
        # Créer 100 patients
        self.create_patients(100)
        
        self.stdout.write(self.style.SUCCESS('Successfully created test data!'))
    
    def create_users(self):
        """Créer 4 utilisateurs de test"""
        users_data = [
            {'username': 'admin', 'email': 'admin@test.com', 'role': 'admin'},
            {'username': 'analyst1', 'email': 'analyst1@test.com', 'role': 'analyst'},
            {'username': 'researcher1', 'email': 'researcher1@test.com', 'role': 'researcher'},
            {'username': 'viewer1', 'email': 'viewer1@test.com', 'role': 'viewer'},
        ]
        
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='test123',
                    role=user_data['role'],
                    organization='Test Hospital'
                )
                # Créer budget epsilon
                EpsilonBudget.objects.get_or_create(user=user)
                self.stdout.write(f"Created user: {user.username}")
    
    def create_patients(self, count):
        """Créer N patients"""
        genders = ['M', 'F', 'O']
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        diagnoses = [
            'Hypertension', 'Diabetes Type 2', 'Asthma', 'Heart Disease',
            'Chronic Pain', 'Arthritis', 'Migraine', 'Depression',
            'Anxiety Disorder', 'Sleep Apnea', 'COPD', 'Cancer',
        ]
        
        patients = []
        for i in range(count):
            admission_date = fake.date_between(start_date='-2y', end_date='today')
            
            patient = Patient(
                age=random.randint(18, 90),
                gender=random.choice(genders),
                zip_code=fake.zipcode()[:10],
                blood_type=random.choice(blood_types),
                weight=round(random.uniform(50, 120), 1),
                height=round(random.uniform(150, 200), 1),
                blood_pressure_systolic=random.randint(90, 180),
                blood_pressure_diastolic=random.randint(60, 110),
                treatment_cost=Decimal(str(round(random.uniform(500, 50000), 2))),
                diagnosis=random.choice(diagnoses),
                admission_date=admission_date,
            )
            patients.append(patient)
        
        # Bulk create
        Patient.objects.bulk_create(patients)
        self.stdout.write(f"Created {count} patients")