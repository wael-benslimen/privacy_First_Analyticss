"""
Génération de données synthétiques de patients
Personne 3 - Data Generation
"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import os

# Initialiser Faker et seed pour reproductibilité
fake = Faker()
np.random.seed(42)

def generate_patient_data(n: int = 5000) -> pd.DataFrame:
    """
    Génère des données synthétiques réalistes de patients
    
    Args:
        n: Nombre de patients à générer (défaut: 5000)
        
    Returns:
        DataFrame avec colonnes: patient_id, age, gender, diagnosis,
        treatment_cost, hospital_stay_days, zipcode, admission_date, 
        bmi, insurance_type
    """
    print(f"Génération de {n} patients synthétiques...")
    
    # ==================== 1. ÂGES ====================
    # Distribution gamma pour des âges réalistes (plus de personnes âgées)
    ages = np.random.gamma(shape=5, scale=10, size=n).astype(int)
    ages = np.clip(ages + 18, 18, 95)  # Entre 18 et 95 ans
    
    # ==================== 2. GENRES ====================
    genders = np.random.choice(
        ['Male', 'Female', 'Other'], 
        n, 
        p=[0.48, 0.48, 0.04]
    )
    
    # ==================== 3. DIAGNOSTICS ====================
    diagnoses = np.random.choice([
        'Diabetes Type 2',
        'Hypertension', 
        'Asthma',
        'Cancer',
        'Heart Disease',
        'COPD',
        'Arthritis',
        'Depression',
        'Anxiety',
        'Healthy Checkup'
    ], n, p=[0.15, 0.20, 0.10, 0.08, 0.12, 0.05, 0.10, 0.08, 0.07, 0.05])
    
    # ==================== 4. COÛTS DE TRAITEMENT ====================
    base_costs = {
        'Diabetes Type 2': 8000,
        'Hypertension': 5000,
        'Asthma': 4000,
        'Cancer': 50000,
        'Heart Disease': 30000,
        'COPD': 15000,
        'Arthritis': 6000,
        'Depression': 3000,
        'Anxiety': 2500,
        'Healthy Checkup': 500
    }
    
    treatment_costs = []
    for age, diagnosis in zip(ages, diagnoses):
        base = base_costs[diagnosis]
        age_factor = 1 + (age - 18) / 100  # Coût augmente avec l'âge
        variation = np.random.uniform(0.7, 1.3)  # Variation ±30%
        cost = base * age_factor * variation
        treatment_costs.append(round(cost, 2))
    
    # ==================== 5. DURÉE D'HOSPITALISATION ====================
    hospital_stays = []
    for diagnosis in diagnoses:
        if diagnosis == 'Cancer':
            stay = max(1, int(np.random.gamma(3, 3)))
        elif diagnosis == 'Heart Disease':
            stay = max(1, int(np.random.gamma(2, 2)))
        elif diagnosis in ['Healthy Checkup', 'Anxiety', 'Depression']:
            stay = 0
        else:
            stay = max(0, int(np.random.gamma(1, 2)))
        hospital_stays.append(min(stay, 30))  # Max 30 jours
    
    # ==================== 6. CODES POSTAUX ====================
    zipcodes = [f"{np.random.randint(10000, 99999)}" for _ in range(n)]
    
    # ==================== 7. DATES D'ADMISSION ====================
    start_date = datetime.now() - timedelta(days=365)
    admission_dates = [
        start_date + timedelta(days=np.random.randint(0, 365))
        for _ in range(n)
    ]
    
    # ==================== 8. BMI ====================
    bmis = []
    for diagnosis in diagnoses:
        if diagnosis in ['Diabetes Type 2', 'Heart Disease', 'Hypertension']:
            bmi = np.random.normal(30, 5)  # BMI plus élevé
        else:
            bmi = np.random.normal(25, 4)
        bmis.append(round(np.clip(bmi, 15, 50), 1))
    
    # ==================== 9. TYPE D'ASSURANCE ====================
    insurance_types = np.random.choice(
        ['Public', 'Private', 'None'], 
        n, 
        p=[0.5, 0.4, 0.1]
    )
    
    # ==================== 10. CRÉER DATAFRAME ====================
    df = pd.DataFrame({
        'patient_id': [f'P{i:05d}' for i in range(1, n+1)],
        'age': ages,
        'gender': genders,
        'diagnosis': diagnoses,
        'treatment_cost': treatment_costs,
        'hospital_stay_days': hospital_stays,
        'zipcode': zipcodes,
        'admission_date': admission_dates,
        'bmi': bmis,
        'insurance_type': insurance_types
    })
    
    print(f"{len(df)} patients générés avec succès!")
    
    return df


def print_statistics(df: pd.DataFrame):
    """Affiche des statistiques sur le dataset"""
    print("\n" + "="*70)
    print("STATISTIQUES DU DATASET")
    print("="*70)
    
    print(f"\nStatistiques générales:")
    print(f"  • Nombre total de patients      : {len(df):,}")
    print(f"  • Âge moyen                     : {df['age'].mean():.1f} ans")
    print(f"  • Âge min/max                   : {df['age'].min()} / {df['age'].max()} ans")
    print(f"  • Coût moyen de traitement      : ${df['treatment_cost'].mean():,.2f}")
    print(f"  • Coût total                    : ${df['treatment_cost'].sum():,.2f}")
    print(f"  • Durée moyenne hospitalisation : {df['hospital_stay_days'].mean():.1f} jours")
    print(f"  • BMI moyen                     : {df['bmi'].mean():.1f}")
    
    print(f"\nDistribution des diagnostics:")
    diag_counts = df['diagnosis'].value_counts()
    for diag, count in diag_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  • {diag:25s}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\nDistribution des genres:")
    gender_counts = df['gender'].value_counts()
    for gender, count in gender_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  • {gender:10s}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\nDistribution des assurances:")
    insurance_counts = df['insurance_type'].value_counts()
    for ins, count in insurance_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  • {ins:10s}: {count:4d} ({percentage:5.1f}%)")
    
    print("="*70)


def save_dataset(df: pd.DataFrame, output_dir: str = '../../data'):
    """
    Sauvegarde le dataset en plusieurs formats
    
    Args:
        df: DataFrame à sauvegarder
        output_dir: Dossier de sortie
    """
    # Créer le dossier s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder en CSV
    csv_path = os.path.join(output_dir, 'patients.csv')
    df.to_csv(csv_path, index=False)
    print(f"CSV sauvegardé: {csv_path}")
    
    # Sauvegarder en JSON
    json_path = os.path.join(output_dir, 'patients.json')
    df.to_json(json_path, orient='records', indent=2, date_format='iso')
    print(f"JSON sauvegardé: {json_path}")
    
    # Sauvegarder statistiques de base
    stats_path = os.path.join(output_dir, 'dataset_stats.txt')
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write("STATISTIQUES DU DATASET\n")
        f.write("="*70 + "\n\n")
        f.write(f"Nombre de patients: {len(df)}\n")
        f.write(f"Âge moyen: {df['age'].mean():.1f} ans\n")
        f.write(f"Coût moyen: ${df['treatment_cost'].mean():.2f}\n")
        f.write(f"Durée moyenne séjour: {df['hospital_stay_days'].mean():.1f} jours\n\n")
        f.write("Distribution diagnostics:\n")
        f.write(df['diagnosis'].value_counts().to_string())
    print(f"Statistiques sauvegardées: {stats_path}")


def generate_and_save(n: int = 5000):
    """Fonction principale: génère et sauvegarde les données"""
    print("\n" + "="*70)
    print("GÉNÉRATION DES DONNÉES SYNTHÉTIQUES")
    print("="*70)
    
    # Générer les données
    df = generate_patient_data(n)
    
    # Afficher les statistiques
    print_statistics(df)
    
    # Sauvegarder
    print("\nSauvegarde des données...")
    save_dataset(df)
    
    print("\n" + "="*70)
    print("GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
    print("="*70)
    print("\nFichiers créés dans le dossier 'data/':")
    print("   • patients.csv")
    print("   • patients.json")
    print("   • dataset_stats.txt")
    
    return df


# ==================== EXÉCUTION ====================
if __name__ == "__main__":
    df = generate_and_save(n=5000)