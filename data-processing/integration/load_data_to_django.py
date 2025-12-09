"""
Script pour charger les données synthétiques dans Django
Personne 3 - Integration Script
"""
import sys
import os
import pandas as pd

# Ajuster le chemin selon votre structure Django
DJANGO_PROJECT_PATH = '../../backend'  # À modifier selon votre structure
sys.path.insert(0, os.path.abspath(DJANGO_PROJECT_PATH))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privacy_analytics.settings')

def setup_django():
    """
    Configure Django pour pouvoir utiliser les models
    """
    try:
        import django
        django.setup()
        print("Django configuré avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de la configuration Django: {e}")
        print("\nVérifiez que:")
        print("1. Le projet Django existe dans le bon dossier")
        print("2. DJANGO_PROJECT_PATH pointe vers le bon endroit")
        print("3. Les models Django sont bien définis")
        return False


def load_patients_from_csv(csv_path='../data/patients.csv'):
    """
    Charge les patients depuis le CSV dans la base Django
    
    Arguments:
        csv_path: Chemin vers le fichier CSV
    """
    if not setup_django():
        return False
    
    # Importer le modèle Patient (après setup Django)
    try:
        from analytics_api.models import Patient
    except ImportError:
        print("Erreur: Le modèle Patient n'existe pas encore")
        print("Personne 2 doit d'abord créer le modèle dans Django")
        return False
    
    # Vérifier que le CSV existe
    if not os.path.exists(csv_path):
        print(f"Erreur: Fichier {csv_path} introuvable")
        return False
    
    # Charger le CSV
    print(f"\nChargement du fichier {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Fichier chargé: {len(df)} lignes")
    
    # Vérifier les colonnes
    required_columns = [
        'patient_id', 'age', 'gender', 'diagnosis', 
        'treatment_cost', 'hospital_stay_days', 'zipcode',
        'admission_date', 'bmi', 'insurance_type'
    ]
    
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        print(f"Erreur: Colonnes manquantes: {missing_columns}")
        return False
    
    print("Toutes les colonnes requises sont présentes")
    
    # Supprimer les anciens patients (optionnel)
    print("\nSuppression des anciens patients...")
    deleted_count = Patient.objects.all().delete()[0]
    print(f"{deleted_count} patients supprimés")
    
    # Créer les patients
    print("\nCréation des nouveaux patients...")
    patients_to_create = []
    
    for index, row in df.iterrows():
        patient = Patient(
            patient_id=row['patient_id'],
            age=int(row['age']),
            gender=row['gender'],
            diagnosis=row['diagnosis'],
            treatment_cost=float(row['treatment_cost']),
            hospital_stay_days=int(row['hospital_stay_days']),
            zipcode=str(row['zipcode']),
            admission_date=pd.to_datetime(row['admission_date']).date(),
            bmi=float(row['bmi']),
            insurance_type=row['insurance_type']
        )
        patients_to_create.append(patient)
        
        # Afficher progression tous les 500 patients
        if (index + 1) % 500 == 0:
            print(f"  Préparé {index + 1}/{len(df)} patients...")
    
    # Insertion en masse (beaucoup plus rapide)
    print("\nInsertion dans la base de données...")
    Patient.objects.bulk_create(patients_to_create, batch_size=500)
    
    # Vérification
    total_patients = Patient.objects.count()
    print(f"\nTerminé! {total_patients} patients dans la base de données")
    
    return True


def verify_data_loaded():
    """
    Vérifie que les données ont bien été chargées
    """
    if not setup_django():
        return
    
    try:
        from analytics_api.models import Patient
    except ImportError:
        print("Le modèle Patient n'existe pas encore")
        return
    
    print("\nVérification des données:")
    print(f"  Nombre total de patients: {Patient.objects.count()}")
    
    # Quelques statistiques
    from django.db.models import Avg, Max, Min, Count
    
    stats = Patient.objects.aggregate(
        avg_age=Avg('age'),
        min_age=Min('age'),
        max_age=Max('age'),
        avg_cost=Avg('treatment_cost')
    )
    
    print(f"  Âge moyen: {stats['avg_age']:.1f} ans")
    print(f"  Âge min/max: {stats['min_age']}/{stats['max_age']} ans")
    print(f"  Coût moyen: ${stats['avg_cost']:,.2f}")
    
    # Distribution des diagnostics
    print("\n  Distribution des diagnostics:")
    diagnoses = Patient.objects.values('diagnosis').annotate(count=Count('diagnosis')).order_by('-count')
    for diag in diagnoses[:5]:
        print(f"    - {diag['diagnosis']}: {diag['count']}")


def generate_django_model_template():
    """
    Génère le code du modèle Django que Personne 2 doit créer
    """
    model_code = """
# Fichier: analytics_api/models.py
# Ce code doit être créé par Personne 2

from django.db import models

class Patient(models.Model):
    patient_id = models.CharField(max_length=10, unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    diagnosis = models.CharField(max_length=100)
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2)
    hospital_stay_days = models.IntegerField()
    zipcode = models.CharField(max_length=10)
    admission_date = models.DateField()
    bmi = models.DecimalField(max_digits=4, decimal_places=1)
    insurance_type = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['patient_id']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['diagnosis']),
            models.Index(fields=['age']),
        ]
    
    def __str__(self):
        return f"{self.patient_id} - {self.diagnosis}"
"""
    
    # Sauvegarder dans un fichier
    with open('django_patient_model.py', 'w') as f:
        f.write(model_code)
    
    print("Template du modèle Django généré: django_patient_model.py")
    print("\nPersonne 2 doit:")
    print("1. Copier ce code dans analytics_api/models.py")
    print("2. Exécuter: python manage.py makemigrations")
    print("3. Exécuter: python manage.py migrate")
    print("4. Ensuite, lancer ce script de chargement")


def main():
    """
    Fonction principale
    """
    print("=" * 70)
    print("Script de chargement des données dans Django")
    print("Personne 3 - Integration")
    print("=" * 70)
    
    print("\nOptions:")
    print("1. Générer le template du modèle Django")
    print("2. Charger les données dans Django")
    print("3. Vérifier les données chargées")
    print("4. Tout faire (générer template + charger + vérifier)")
    
    choice = input("\nVotre choix (1-4): ").strip()
    
    if choice == '1':
        generate_django_model_template()
    
    elif choice == '2':
        csv_path = input("\nChemin vers patients.csv (Enter pour défaut): ").strip()
        if not csv_path:
            csv_path = '../data/patients.csv'
        load_patients_from_csv(csv_path)
    
    elif choice == '3':
        verify_data_loaded()
    
    elif choice == '4':
        print("\n--- Étape 1: Génération du template ---")
        generate_django_model_template()
        
        input("\nAppuyez sur Enter après que Personne 2 ait créé le modèle...")
        
        print("\n--- Étape 2: Chargement des données ---")
        if load_patients_from_csv():
            print("\n--- Étape 3: Vérification ---")
            verify_data_loaded()
    
    else:
        print("Choix invalide")
    
    print("\n" + "=" * 70)
    print("Terminé")
    print("=" * 70)


if __name__ == "__main__":
    main()