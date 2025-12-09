import os
import sys
import random
import uuid
import django
from faker import Faker
from datetime import timedelta
from decimal import Decimal

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Patient

fake = Faker()

def create_fake_patients(count=100):
    print(f"Generating {count} fake patient records...")
    
    patients = []
    
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    genders = ['M', 'F', 'O']
    
    for i in range(count):
        # Generate improved realistic data
        age = random.randint(18, 90)
        
        # Correlate some health metrics with age/gender for slightly more realistic data distributions
        gender = random.choice(genders)
        
        # Weight roughly based on height (BMI logic)
        height = random.uniform(150, 200) if gender == 'M' else random.uniform(145, 180)
        base_weight = 22 * ((height/100) ** 2) # Base BMI 22
        weight = random.uniform(base_weight * 0.8, base_weight * 1.5)
        
        # Blood pressure roughly correlated with age
        systolic = random.randint(90, 140) + (age // 5)
        diastolic = random.randint(60, 90) + (age // 10)
        
        patient = Patient(
            patient_id=str(uuid.uuid4()),
            age=age,
            gender=gender,
            zip_code=fake.zipcode(),
            blood_type=random.choice(blood_types),
            weight=round(weight, 1),
            height=round(height, 1),
            blood_pressure_systolic=systolic,
            blood_pressure_diastolic=diastolic,
            treatment_cost=Decimal(random.uniform(100.0, 50000.0)).quantize(Decimal("0.01")),
            diagnosis=fake.sentence(nb_words=3).replace('.', ''),
            admission_date=fake.date_between(start_date='-2y', end_date='today')
        )
        patients.append(patient)
        
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} records...")

    print("Bulk creating records in database...")
    Patient.objects.bulk_create(patients)
    print(f"Successfully created {count} patient records!")

if __name__ == '__main__':
    # Allow passing count as argument
    count = 100
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Invalid count, using default 100")
            
    create_fake_patients(count)
