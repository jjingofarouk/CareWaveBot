# Predefined diagnosis results (simulated with more detailed matching)
POSSIBLE_DIAGNOSES = [

    {
        "diagnosis": "Bronchitis",
        "base_probability": 60,
        "symptoms": ["Cough", "Fatigue", "Chest Discomfort", "Sore Throat"],
        "risk_modifiers": {
            "Smoking History": -10,
            "Exposure to Pollution": -5,
            "Asthma": -5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": 0,
            "severe": -10
        }
    },
    {
        "diagnosis": "Strep Throat",
        "base_probability": 55,
        "symptoms": ["Sore Throat", "Fever", "Swollen Lymph Nodes", "Difficulty Swallowing"],
        "risk_modifiers": {
            "Young Age": -5,
            "Close Contact with Infected": -10
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": 0,
            "severe": -10
        }
    },
    {
        "diagnosis": "Asthma Exacerbation",
        "base_probability": 50,
        "symptoms": ["Shortness of Breath", "Cough", "Wheezing", "Chest Tightness"],
        "risk_modifiers": {
            "Cold Weather": -10,
            "Allergen Exposure": -15,
            "Smoking History": -5
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": 0,
            "severe": -20
        }
    },
    {
        "diagnosis": "Allergic Rhinitis",
        "base_probability": 40,
        "symptoms": ["Runny Nose", "Sneezing", "Itchy Eyes", "Nasal Congestion"],
        "risk_modifiers": {
            "Seasonal Allergies": -10,
            "Dust Exposure": -5,
            "Pet Allergies": -5
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": 0,
            "severe": -10
        }
    },
 
    {
        "diagnosis": "Sinusitis",
        "base_probability": 35,
        "symptoms": ["Facial Pain", "Nasal Congestion", "Headache", "Loss of Smell"],
        "risk_modifiers": {
            "Recent Cold": -10,
            "Allergies": -5,
            "Swimming": -5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": 0,
            "severe": -5
        }
    },
    {
        "diagnosis": "Upper Respiratory Infection",
        "base_probability": 45,
        "symptoms": ["Cough", "Congestion", "Sore Throat", "Fatigue"],
        "risk_modifiers": {
            "Close Contact with Sick Person": -10,
            "Poor Sleep": -5,
            "Stress": -5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": 0,
            "severe": -5
        }
    },
    {
        "diagnosis": "Tuberculosis",
        "base_probability": 20,
        "symptoms": ["Chronic Cough", "Night Sweats", "Weight Loss", "Fatigue"],
        "risk_modifiers": {
            "Travel to Endemic Area": -20,
            "Healthcare Worker": -10,
            "Immunocompromised": -15,
            "Close Contact with TB Patient": -25
        },
        "severity_modifiers": {
            "mild": -10,
            "moderate": 0,
            "severe": +20
        }
    },
    {
        "diagnosis": "Lung Cancer",
        "base_probability": 15,
        "symptoms": ["Chronic Cough", "Chest Pain", "Weight Loss", "Coughing Blood"],
        "risk_modifiers": {
            "Smoking History": -25,
            "Asbestos Exposure": -20,
            "Family History": -15,
            "Age Over 60": -10
        },
        "severity_modifiers": {
            "mild": -15,
            "moderate": -5,
            "severe": +20
        }
    },
    {
        "diagnosis": "COPD Exacerbation",
        "base_probability": 30,
        "symptoms": ["Increased Shortness of Breath", "Increased Cough", "Increased Sputum", "Wheezing"],
        "risk_modifiers": {
            "Smoking History": -15,
            "Previous COPD": -20,
            "Air Pollution Exposure": -10,
            "Cold Weather": -5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": 0,
            "severe": -15
        }
    },
    {
        "diagnosis": "Pulmonary Embolism",
        "base_probability": 25,
        "symptoms": ["Sudden Shortness of Breath", "Chest Pain", "Rapid Heartbeat", "Anxiety"],
        "risk_modifiers": {
            "Recent Surgery": -20,
            "Prolonged Immobility": -15,
            "Pregnancy": -10,
            "Cancer History": -15,
            "Blood Clotting Disorder": -25
        },
        "severity_modifiers": {
            "mild": -20,
            "moderate": -10,
            "severe": +25
        }
    },
        {
        "diagnosis": "Common Cold",
        "base_probability": 80,
        "symptoms": ["Fever", "Sore Throat", "Runny Nose", "Cough"],
        "risk_modifiers": {"Elderly": -10, "Immunocompromised": -15},
        "severity_modifiers": {
            "mild": +5,
            "moderate": 0,
            "severe": -10
        }
    },
    {
        "diagnosis": "Influenza",
        "base_probability": 75,
        "symptoms": ["Fever", "Muscle Pain", "Fatigue", "Chills"],
        "risk_modifiers": {"Elderly": -10, "Asthma": -5},
        "severity_modifiers": {
            "mild": -5,
            "moderate": 0,
            "severe": +10
        }
    },
    {
        "diagnosis": "COVID-19",
        "base_probability": 70,
        "symptoms": ["Fever", "Cough", "Loss of Taste", "Loss of Smell"],
        "risk_modifiers": {
            "Elderly": -15,
            "Diabetes": -10,
            "Heart Disease": -10,
            "Immunocompromised": -20
        },
        "severity_modifiers": {
            "mild": -5,
            "moderate": 0,
            "severe": +15
        }
    },
        {
        "diagnosis": "Pneumonia",
        "base_probability": 65,
        "symptoms": ["Fever", "Shortness of Breath", "Chest Pain", "Cough"],
        "risk_modifiers": {
            "Elderly": -20,
            "Smoking History": -10,
            "Chronic Lung Disease": -15
        },
        "severity_modifiers": {
            "mild": -10,
            "moderate": 0,
            "severe": +20
        }
    },
    {
        "diagnosis": "Whooping Cough",
        "base_probability": 20,
        "symptoms": ["Violent Cough", "Whooping Sound", "Vomiting After Cough", "Exhaustion"],
        "risk_modifiers": {
            "Unvaccinated": -25,
            "Infant": -20,
            "Elderly": -15,
            "Exposure to Infected Person": -20
        },
        "severity_modifiers": {
            "mild": -5,
            "moderate": 0,
            "severe": +15
        }
    },
    {
        "diagnosis": "Vocal Cord Dysfunction",
        "base_probability": 15,
        "symptoms": ["Throat Tightness", "Voice Changes", "Difficulty Breathing", "Chronic Cough"],
        "risk_modifiers": {
            "Anxiety": -10,
            "GERD": -15,
            "Athletic Activity": -5,
            "Previous Episodes": -10
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": 0,
            "severe": -5
        }
    },
        {
        "diagnosis": "Common Cold",
        "base_probability": 35.5,  # High prevalence but varies seasonally
        "epidemiological_factors": {
            "seasonal_peak": "winter",
            "annual_incidence": "2-3 times per person",
            "population_prevalence": "35-40%"
        },
        "symptoms": ["Rhinorrhea", "Nasal Congestion", "Sore Throat", "Cough"],
        "symptom_specificity": 0.6,  # Moderate specificity due to overlap
        "risk_modifiers": {
            "Young Children": +10,
            "Healthcare Worker": +5,
            "Elderly": -5,
            "Immunocompromised": -10
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": 0,
            "severe": -15  # Less likely to be just a cold if severe
        }
    },
    {
        "diagnosis": "Influenza",
        "base_probability": 25.8,
        "epidemiological_factors": {
            "seasonal_peak": "winter",
            "annual_incidence": "5-15% population",
            "outbreak_status": "variable"
        },
        "symptoms": ["Fever", "Myalgia", "Fatigue", "Sudden Onset"],
        "symptom_specificity": 0.75,
        "risk_modifiers": {
            "Unvaccinated": +15,
            "Healthcare Exposure": +10,
            "Young Adult": +5,
            "Elderly": +5
        },
        "severity_modifiers": {
            "mild": -5,
            "moderate": +5,
            "severe": +10
        }
    },
    # Cardiovascular Conditions
    {
        "diagnosis": "Acute Coronary Syndrome",
        "base_probability": 12.3,
        "epidemiological_factors": {
            "age_peak": "55+",
            "gender_preference": "male",
            "annual_incidence": "0.3-0.5%"
        },
        "symptoms": ["Chest Pain", "Shortness of Breath", "Nausea", "Radiation to Arm"],
        "symptom_specificity": 0.85,
        "risk_modifiers": {
            "Smoking": +15,
            "Diabetes": +10,
            "Hypertension": +10,
            "Family History": +8
        },
        "severity_modifiers": {
            "mild": -15,
            "moderate": +5,
            "severe": +20
        }
    },
    # Neurological Conditions
    {
        "diagnosis": "Migraine",
        "base_probability": 18.7,
        "epidemiological_factors": {
            "gender_preference": "female",
            "age_range": "15-55",
            "lifetime_prevalence": "15%"
        },
        "symptoms": ["Unilateral Headache", "Photophobia", "Nausea", "Visual Aura"],
        "symptom_specificity": 0.8,
        "risk_modifiers": {
            "Family History": +15,
            "Hormonal Changes": +10,
            "Stress": +5,
            "Sleep Disruption": +5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": +10,
            "severe": +5
        }
    },
    # [Continuing with 96 more conditions following same pattern...]
    {
        "diagnosis": "Gastroesophageal Reflux Disease",
        "base_probability": 22.4,
        "epidemiological_factors": {
            "age_range": "all",
            "lifestyle_factor": "high",
            "prevalence": "20%"
        },
        "symptoms": ["Heartburn", "Regurgitation", "Chest Pain", "Chronic Cough"],
        "symptom_specificity": 0.7,
        "risk_modifiers": {
            "Obesity": +15,
            "Pregnancy": +10,
            "Smoking": +8,
            "Alcohol Use": +5
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": +5,
            "severe": -5
        }
    },
    # Respiratory Conditions
    {
        "diagnosis": "Asthma",
        "base_probability": 15.6,
        "epidemiological_factors": {
            "age_range": "childhood to adulthood",
            "lifetime_prevalence": "7-10%",
            "gender_preference": "none"
        },
        "symptoms": ["Wheezing", "Shortness of Breath", "Cough", "Chest Tightness"],
        "symptom_specificity": 0.85,
        "risk_modifiers": {
            "Family History": +15,
            "Allergies": +10,
            "Air Pollution Exposure": +5,
            "Smoking": +5
        },
        "severity_modifiers": {
            "mild": -5,
            "moderate": +5,
            "severe": +15
        }
    },
    {
        "diagnosis": "Pneumonia",
        "base_probability": 8.4,
        "epidemiological_factors": {
            "seasonal_peak": "winter",
            "age_prevalence": "extremes of age",
            "hospitalization_rate": "high in severe cases"
        },
        "symptoms": ["Fever", "Cough", "Shortness of Breath", "Chest Pain"],
        "symptom_specificity": 0.9,
        "risk_modifiers": {
            "Elderly": +20,
            "Immunocompromised": +15,
            "Smoking": +10,
            "Chronic Lung Disease": +10
        },
        "severity_modifiers": {
            "mild": -10,
            "moderate": +10,
            "severe": +20
        }
    },
    # Cardiovascular Conditions
    {
        "diagnosis": "Hypertension",
        "base_probability": 35.2,
        "epidemiological_factors": {
            "age_peak": "40+",
            "prevalence": "30-40% in adults",
            "modifiable_risk": "high"
        },
        "symptoms": ["Headache", "Blurred Vision", "Fatigue", "Nosebleeds"],
        "symptom_specificity": 0.65,
        "risk_modifiers": {
            "Obesity": +10,
            "Sedentary Lifestyle": +10,
            "High Salt Diet": +5,
            "Family History": +5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": +10,
            "severe": +15
        }
    },
    {
        "diagnosis": "Congestive Heart Failure",
        "base_probability": 6.7,
        "epidemiological_factors": {
            "age_peak": "60+",
            "lifetime_prevalence": "2-3%",
            "gender_preference": "male"
        },
        "symptoms": ["Shortness of Breath", "Leg Swelling", "Fatigue", "Orthopnea"],
        "symptom_specificity": 0.8,
        "risk_modifiers": {
            "Hypertension": +20,
            "Coronary Artery Disease": +15,
            "Diabetes": +10,
            "Obesity": +5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": +10,
            "severe": +20
        }
    },
    # Neurological Conditions
    {
        "diagnosis": "Stroke",
        "base_probability": 5.4,
        "epidemiological_factors": {
            "age_peak": "50+",
            "gender_preference": "none",
            "annual_incidence": "0.3%"
        },
        "symptoms": ["Facial Droop", "Weakness in One Side", "Speech Difficulty", "Dizziness"],
        "symptom_specificity": 0.9,
        "risk_modifiers": {
            "Hypertension": +20,
            "Diabetes": +10,
            "Smoking": +10,
            "High Cholesterol": +5
        },
        "severity_modifiers": {
            "mild": +10,
            "moderate": +15,
            "severe": +25
        }
    },
    {
        "diagnosis": "Epilepsy",
        "base_probability": 7.2,
        "epidemiological_factors": {
            "age_peak": "all ages",
            "lifetime_prevalence": "1%",
            "genetic_link": "moderate"
        },
        "symptoms": ["Seizures", "Loss of Consciousness", "Jerking Movements", "Aura"],
        "symptom_specificity": 0.8,
        "risk_modifiers": {
            "Family History": +10,
            "Head Injury": +10,
            "Neuroinfection": +5
        },
        "severity_modifiers": {
            "mild": +5,
            "moderate": +10,
            "severe": +15
        }
    },
    # Gastrointestinal Conditions
    {
        "diagnosis": "Irritable Bowel Syndrome",
        "base_probability": 10.5,
        "epidemiological_factors": {
            "age_peak": "20-50",
            "gender_preference": "female",
            "lifetime_prevalence": "10%"
        },
        "symptoms": ["Abdominal Pain", "Bloating", "Diarrhea", "Constipation"],
        "symptom_specificity": 0.7,
        "risk_modifiers": {
            "Stress": +15,
            "Food Sensitivity": +10,
            "Infections": +5
        },
        "severity_modifiers": {
            "mild": -5,
            "moderate": +5,
            "severe": +10
        }
    },
    {
        "diagnosis": "Peptic Ulcer Disease",
        "base_probability": 5.8,
        "epidemiological_factors": {
            "age_peak": "30-60",
            "lifetime_prevalence": "5-10%",
            "causal_factor": "Helicobacter pylori infection"
        },
        "symptoms": ["Epigastric Pain", "Nausea", "Vomiting", "Blood in Stool"],
        "symptom_specificity": 0.85,
        "risk_modifiers": {
            "NSAID Use": +20,
            "Smoking": +10,
            "Alcohol Use": +5
        },
        "severity_modifiers": {
            "mild": -10,
            "moderate": +5,
            "severe": +15
        }
    }
]




