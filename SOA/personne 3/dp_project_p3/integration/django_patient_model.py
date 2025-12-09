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
