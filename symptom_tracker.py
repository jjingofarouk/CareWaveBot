from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from typing import Dict, List, Union, Optional
from dataclasses import dataclass
import json

# Import all necessary modules
import symptom_combinations
import symptom_list
import drug_history_weights
from risk_factor_weights import risk_factor_weights
import travel_risk_factors
import symptom_weights

# Conversation states
(ENTER_AGE, ENTER_GENDER, ENTER_SYMPTOMS, ENTER_DURATION, 
 ENTER_DURATION_UNIT, ENTER_SEVERITY, ENTER_TRAVEL, 
 ENTER_TRAVEL_DATES, ENTER_MEDICATIONS, CONFIRM) = range(10)

# Diagnosis confidence thresholds
CONFIDENCE_THRESHOLDS = {
    'HIGH': 0.7,
    'MEDIUM': 0.4
}

@dataclass
class DiagnosisFactors:
    symptoms: List[str]
    risks: List[str]
    travel: Optional[str]

@dataclass
class DiagnosisResult:
    diagnosis: str
    probability: float
    confidence: str
    matching_factors: Dict[str, str]

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current operation"""
    await update.message.reply_text(
        "Operation cancelled. Use /track to start again or /help for other options.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

class SymptomTracker:
    def __init__(self):
        self.symptom_list = symptom_list
        self.symptom_combinations = symptom_combinations
        self.calculator = DiagnosisCalculator()
        
    async def start_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the symptom tracking process"""
        context.user_data['patient_info'] = {}
        await update.message.reply_text(
            "Let's track your symptoms. First, please enter your age:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ENTER_AGE

    async def handle_age(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle age input"""
        age = update.message.text
        if not age.isdigit() or int(age) < 0 or int(age) > 120:
            await update.message.reply_text("Please enter a valid age between 0 and 120:")
            return ENTER_AGE
            
        context.user_data['patient_info']['age'] = age
        
        reply_markup = ReplyKeyboardMarkup([
            ['Male', 'Female', 'Other']
        ], one_time_keyboard=True)
        
        await update.message.reply_text(
            "Please select your gender:",
            reply_markup=reply_markup
        )
        return ENTER_GENDER

    async def handle_gender(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle gender input"""
        context.user_data['patient_info']['gender'] = update.message.text
        
        await update.message.reply_text(
            "Please enter your symptoms one at a time. Use /done when finished."
        )
        return ENTER_SYMPTOMS

    async def handle_symptoms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle symptom input"""
        if 'symptoms' not in context.user_data['patient_info']:
            context.user_data['patient_info']['symptoms'] = []
            
        symptom = update.message.text
        
        if symptom in self.symptom_combinations:
            new_symptoms = [s for s in self.symptom_combinations[symptom] 
                          if s not in context.user_data['patient_info']['symptoms']]
            context.user_data['patient_info']['symptoms'].extend(new_symptoms)
            await update.message.reply_text(
                f"Added symptom combination: {', '.join(new_symptoms)}\n"
                "Enter another symptom or use /done when finished"
            )
        elif symptom in self.symptom_list:
            if symptom not in context.user_data['patient_info']['symptoms']:
                context.user_data['patient_info']['symptoms'].append(symptom)
                await update.message.reply_text(
                    f"Added: {symptom}\n"
                    "Enter another symptom or use /done when finished"
                )
            else:
                await update.message.reply_text(
                    "This symptom is already in your list.\n"
                    "Enter another symptom or use /done when finished"
                )
        else:
            suggestions = [s for s in self.symptom_list 
                         if symptom.lower() in s.lower()][:5]
            
            if suggestions:
                keyboard = [[InlineKeyboardButton(s, callback_data=f"symptom:{s}")] 
                          for s in suggestions]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "Did you mean one of these?",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    "Symptom not found. Please try again or use /done when finished"
                )
        return ENTER_SYMPTOMS

    async def handle_done_symptoms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle completion of symptom entry"""
        if not context.user_data['patient_info'].get('symptoms'):
            await update.message.reply_text(
                "Please enter at least one symptom before proceeding."
            )
            return ENTER_SYMPTOMS

        await update.message.reply_text(
            "How long have you been experiencing these symptoms? Please enter a number:"
        )
        return ENTER_DURATION

    async def handle_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle duration input"""
        duration = update.message.text
        if not duration.isdigit() or int(duration) <= 0:
            await update.message.reply_text("Please enter a valid positive number:")
            return ENTER_DURATION

        context.user_data['patient_info']['duration'] = duration

        reply_markup = ReplyKeyboardMarkup([
            ['Days', 'Weeks', 'Months']
        ], one_time_keyboard=True)

        await update.message.reply_text(
            "Please select the duration unit:",
            reply_markup=reply_markup
        )
        return ENTER_DURATION_UNIT

    async def handle_duration_unit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle duration unit input"""
        context.user_data['patient_info']['duration_unit'] = update.message.text.lower()

        reply_markup = ReplyKeyboardMarkup([
            ['Mild', 'Moderate', 'Severe']
        ], one_time_keyboard=True)

        await update.message.reply_text(
            "How would you rate the severity of your symptoms?",
            reply_markup=reply_markup
        )
        return ENTER_SEVERITY

    async def handle_severity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle severity input"""
        context.user_data['patient_info']['severity'] = update.message.text.lower()
        return await self.handle_travel(update, context)

    async def handle_travel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle travel history input"""
        reply_markup = ReplyKeyboardMarkup([
            ['Yes', 'No']
        ], one_time_keyboard=True)
        
        await update.message.reply_text(
            "Have you traveled anywhere in the last 3 months?",
            reply_markup=reply_markup
        )
        return ENTER_TRAVEL_DATES

    async def handle_travel_dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle travel dates input"""
        response = update.message.text
        context.user_data['patient_info']['has_traveled'] = response.lower() == 'yes'
        
        if response.lower() == 'yes':
            await update.message.reply_text(
                "Please enter the places you visited and dates (e.g., 'Paris 1-15 Jan, Rome 16-20 Jan'):"
            )
            return ENTER_MEDICATIONS
        else:
            context.user_data['patient_info']['travel_history'] = "None"
            return await self.handle_medications(update, context)

    async def handle_medications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle medications input"""
        if context.user_data['patient_info'].get('has_traveled'):
            context.user_data['patient_info']['travel_history'] = update.message.text
            
        await update.message.reply_text(
            "Are you currently taking any medications? If yes, please list them. If no, type 'None':"
        )
        return CONFIRM

    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle final confirmation and calculate diagnosis"""
        if 'medications' not in context.user_data['patient_info']:
            context.user_data['patient_info']['medications'] = update.message.text

        response = update.message.text.lower()
        
        if response != 'yes':
            await update.message.reply_text(
                "Let's start over. Use /track to begin again.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

        # Calculate diagnosis
        info = context.user_data['patient_info']
        diagnosis_result = self.calculator.calculate_diagnosis(
            symptoms=info['symptoms'],
            duration=int(info['duration']),
            duration_unit=info['duration_unit'],
            severity=info['severity'],
            age=int(info['age']),
            gender=info['gender'],
            drug_history=info['medications'] if info['medications'] != 'None' else None,
            travel_region=info['travel_history'] if info['travel_history'] != 'None' else None
        )

        if 'error' in diagnosis_result:
            await update.message.reply_text(
                f"Error in diagnosis: {diagnosis_result['error']}",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            # Format top 5 diagnoses
            diagnoses = diagnosis_result['detailed'][:5]
            response_text = "Top 5 Possible Diagnoses:\n\n"
            
            for i, result in enumerate(diagnoses, 1):
                response_text += (
                    f"{i}. {result.diagnosis}\n"
                    f"   Probability: {result.probability}%\n"
                    f"   Confidence: {result.confidence}\n"
                    f"   Matching Symptoms: {result.matching_factors['symptom_match']}\n"
                    f"   Risk Factors: {result.matching_factors['risk_factor_match']}\n"
                    f"   Travel Risks: {result.matching_factors['travel_risk_match']}\n\n"
                )

            await update.message.reply_text(
                response_text,
                reply_markup=ReplyKeyboardRemove()
            )

        return ConversationHandler.END

    def get_conversation_handler(self) -> ConversationHandler:
        """Return the conversation handler for the symptom tracker"""
        return ConversationHandler(
            entry_points=[CommandHandler('track', self.start_tracking)],
            states={
                ENTER_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_age)],
                ENTER_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_gender)],
                ENTER_SYMPTOMS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_symptoms),
                    CommandHandler('done', self.handle_done_symptoms)
                ],
                ENTER_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_duration)],
                ENTER_DURATION_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_duration_unit)],
                ENTER_SEVERITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_severity)],
                ENTER_TRAVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_travel)],
                ENTER_TRAVEL_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_travel_dates)],
                ENTER_MEDICATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_medications)],
                CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_confirmation)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

class DiagnosisCalculator:
    def calculate_diagnosis(self, **kwargs) -> Dict:
        """Calculate diagnosis based on symptoms and other factors"""
        return calculate_diagnosis(**kwargs)

def calculate_diagnosis(
    symptoms: List[str],
    duration: int,
    duration_unit: str,
    severity: str,
    age: int,
    gender: str,
    drug_history: Optional[Union[str, List[str]]] = None,
    travel_region: Optional[str] = None,
    risk_factors: Optional[List[str]] = None
) -> Dict[str, Union[List[DiagnosisResult], str]]:
    """
    Calculates diagnosis based on symptoms and other factors
    """
    try:
        # Input validation
        if not symptoms:
            return {'error': 'Please select at least one symptom'}

        # Normalize duration to days
        normalized_duration = normalize_duration(duration, duration_unit)
        age_group = categorize_age(age)

        # Calculate scores using both combination and individual approaches
        diagnosis_scores = calculate_complete_scores(symptoms, {
            'duration': normalized_duration,
            'severity': severity,
            'age_group': age_group,
            'gender': gender
        })

        # Apply additional factor weights
        apply_travel_risks(diagnosis_scores, travel_region)
        apply_drug_history(diagnosis_scores, drug_history)
        apply_risk_factors(diagnosis_scores, risk_factors)

        # Filter out diagnoses with zero scores
        filtered_scores = {
            disease: data for disease, data in diagnosis_scores.items()
            if data['score'] > 0
        }

        if not filtered_scores:
            return {'error': 'No matching diagnoses found for the given symptoms'}

        results = calculate_final_results(filtered_scores, symptoms, {
            'travel_region': travel_region,
            'risk_factors': risk_factors
        })

        return {
            'detailed': [
                DiagnosisResult(
                    diagnosis=result['disease'],
                    probability=round(result['probability'] * 100),
                    confidence=get_confidence_level(result['probability']),
                    matching_factors={
                        'symptom_match': ', '.join(result['factors'].symptoms),
                        'risk_factor_match': ', '.join(result['factors'].risks),
                        'travel_risk_match': result['factors'].travel or 'None'
                    }
                )
                for result in results
            ]
        }

    except Exception as error:
        print(f'Calculation error: {str(error)}')
        return {'error': f'Error calculating diagnosis: {str(error)}'}

def calculate_complete_scores(
    symptoms: List[str],
    factors: Dict[str, Union[int, str]]
) -> Dict[str, Dict]:
    """Calculates complete scores using both combination and individual approaches"""
    scores = {}
    
    # First try exact combinations
    exact_matches = find_exact_matches(symptoms)
    if exact_matches:
        scores.update(exact_matches)

    # Then try partial combinations
    partial_matches = find_partial_matches(symptoms)
    merge_scores(scores, partial_matches)

    # Finally, evaluate individual symptoms
    individual_scores = calculate_individual_scores(symptoms, factors)
    merge_scores(scores, individual_scores)

    return scores

def find_exact_matches(symptoms: List[str]) -> Dict:
    """Finds exact matches in symptom combinations"""
    sorted_symptoms = ', '.join(sorted(symptoms))
    if sorted_symptoms in symptom_combinations:
        matches = {}
        for disease, weight in symptom_combinations[sorted_symptoms].items():
            matches[disease] = {
                'score': weight,
                'matching_symptoms': symptoms,
                'is_exact_match': True
            }
        return matches
    return {}

def find_partial_matches(symptoms: List[str]) -> Dict:
    """Finds partial matches in symptom combinations"""
    matches = {}
    symptom_set = set(symptoms)

    for combination, diseases in symptom_combinations.items():
        combination_symptoms = combination.split(', ')
        intersection = [s for s in combination_symptoms if s in symptom_set]
        
        if len(intersection) >= min(2, len(combination_symptoms)):
            match_ratio = len(intersection) / len(combination_symptoms)
            
            for disease, weight in diseases.items():
                if disease not in matches:
                    matches[disease] = {
                        'score': 0,
                        'matching_symptoms': []
                    }
                matches[disease]['score'] += weight * match_ratio
                matches[disease]['matching_symptoms'].extend(intersection)

    return matches

def calculate_individual_scores(
    symptoms: List[str],
    factors: Dict[str, Union[int, str]]
) -> Dict:
    """Calculates scores based on individual symptoms"""
    scores = {}
    
    for symptom in symptoms:
        if symptom in symptom_weights:
            for disease, data in symptom_weights[symptom].items():
                if disease not in scores:
                    scores[disease] = {
                        'score': 0,
                        'matching_symptoms': []
                    }
                
                base_score = data['weight']
                modifiers = calculate_modifiers(data, factors)
                scores[disease]['score'] += base_score * modifiers
                scores[disease]['matching_symptoms'].append(symptom)

    return scores

def merge_scores(target: Dict, source: Dict) -> None:
    """Merges score objects, combining matching symptoms and adding scores"""
    for disease, data in source.items():
        if disease not in target:
            target[disease] = {
                'score': 0,
                'matching_symptoms': []
            }
        target[disease]['score'] += data['score']
        target[disease]['matching_symptoms'] = list(set(
            target[disease]['matching_symptoms'] + data['matching_symptoms']
        ))

def normalize_duration(duration: int, unit: str) -> int:
    """Normalizes duration to days"""
    multipliers = {
        'days': 1,
        'weeks': 7,
        'months': 30
    }
    return duration * multipliers.get(unit.lower(), 1)

def categorize_age(age: int) -> str:
    """Categorizes age into groups"""
    if age <= 12:
        return 'child'
    if age <= 18:
        return 'adolescent'
    if age <= 65:
        return 'adult'
    return 'elderly'

def calculate_modifiers(data: Dict, factors: Dict) -> float:
    """Calculates modifiers based on various factors"""
    return (
        data.get('duration_factors', {}).get(factors['duration'], 1) *
        data.get('severity_factors', {}).get(factors['severity'], 1) *
        data.get('age_factors', {}).get(factors['age_group'], 1) *
        data.get('gender_factors', {}).get(factors['gender'], 1)
    )

def apply_travel_risks(scores: Dict, region: Optional[str]) -> None:
    """Applies travel risk factors to scores"""
    if not region or region not in travel_risk_factors:
        return

    for disease, weight in travel_risk_factors[region].items():
        if disease not in scores:
            scores[disease] = {'score': 0, 'matching_symptoms': []}
        scores[disease]['score'] += weight
        scores[disease]['travel_risk'] = region

def apply_drug_history(
    scores: Dict,
    drugs: Optional[Union[str, List[str]]]
) -> None:
    """Applies drug history factors to scores"""
    if not drugs:
        return
    
    drug_list = [drugs] if isinstance(drugs, str) else drugs
    for drug in drug_list:
        if drug in drug_history_weights:
            for disease, weight in drug_history_weights[drug].items():
                if disease not in scores:
                    scores[disease] = {'score': 0, 'matching_symptoms': []}
                scores[disease]['score'] += weight

def apply_risk_factors(scores: Dict, factors: Optional[List[str]]) -> None:
    """Applies general risk factors to scores"""
    if not factors:
        return

    for factor in factors:
        if factor in risk_factor_weights:
            for disease, weight in risk_factor_weights[factor].items():
                if disease not in scores:
                    scores[disease] = {'score': 0, 'matching_symptoms': []}
                scores[disease]['score'] += weight
                if 'risk_factors' not in scores[disease]:
                    scores[disease]['risk_factors'] = []
                scores[disease]['risk_factors'].append(factor)

def calculate_final_results(
    scores: Dict,
    symptoms: List[str],
    factors: Dict[str, Optional[Union[str, List[str]]]]
) -> List[Dict]:
    """Calculates final diagnostic results with probabilities"""
    total_score = sum(data['score'] for data in scores.values())
    
    results = []
    for disease, data in scores.items():
        probability = data['score'] / total_score if total_score > 0 else 0
        results.append({
            'disease': disease,
            'probability': probability,
            'factors': DiagnosisFactors(
                symptoms=list(set(data['matching_symptoms'])),
                risks=data.get('risk_factors', []),
                travel=data.get('travel_risk')
            )
        })
    
    return sorted(results, key=lambda x: x['probability'], reverse=True)

def get_confidence_level(probability: float) -> str:
    """Determines confidence level based on probability"""
    if probability >= CONFIDENCE_THRESHOLDS['HIGH']:
        return 'High'
    if probability >= CONFIDENCE_THRESHOLDS['MEDIUM']:
        return 'Medium'
    return 'Low'

def setup_bot(application):
    """Setup the bot with the symptom tracking system"""
    tracker = SymptomTracker()
    application.add_handler(tracker.get_conversation_handler())