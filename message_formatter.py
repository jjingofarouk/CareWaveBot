from typing import Dict, List

class MessageFormatter:
    @staticmethod
    async def format_diagnosis_result(diagnosis_result: List[Dict]) -> str:
        """Format the diagnosis results into a readable message"""
        message = "🏥 Top Possible Diagnoses:\n\n"
        
        for i, result in enumerate(diagnosis_result[:5], 1):
            message += f"{i}. 🔍 {result.get('diagnosis', 'Unknown')}\n"
            
            # Add probability if available
            if 'probability' in result:
                message += f"   └ Probability: {result['probability']}%\n"
            
            # Add confidence if available
            if 'confidence' in result:
                message += f"   └ Confidence: {result['confidence']}%\n"
            
            # Safely access matching factors
            matching_factors = result.get('matching_factors', {})
            
            # Add symptoms if available
            symptoms = matching_factors.get('symptom_match', [])
            if symptoms:
                if isinstance(symptoms, list):
                    symptom_text = ", ".join(symptoms)
                else:
                    symptom_text = str(symptoms)
                message += f"   └ Matching Symptoms: {symptom_text}\n"
            
            # Add risk factors if available
            risk_factors = matching_factors.get('risk_factor_match', [])
            if risk_factors:
                if isinstance(risk_factors, list):
                    risk_text = ", ".join(risk_factors)
                else:
                    risk_text = str(risk_factors)
                message += f"   └ Risk Factors: {risk_text}\n"
            
            # Add travel history if available
            travel_risk = matching_factors.get('travel_risk_match', 'No')
            if travel_risk and travel_risk != 'No':
                message += f"   └ Travel History: {travel_risk}\n"
            
            message += "\n"
        
        message += (
            "⚠️ IMPORTANT: These results are for informational purposes only.\n"
            "Please consult a healthcare provider for proper medical diagnosis and treatment."
        )
        
        return message

    @staticmethod
    def get_welcome_message() -> str:
        return (
            "👋 Hello! I am your Health Information Assistant.\n\n"
            "⚠️ IMPORTANT: I provide general health information only. "
            "For medical concerns, please consult a qualified healthcare provider.\n\n"
            "I will help you check possible diagnoses based on your symptoms.\n\n"
            "Let's begin! I'll need some details from you.\n"
            "You can type /cancel at any time to stop."
        )

    @staticmethod
    def get_symptom_prompt(common_symptoms: List[str]) -> str:
        symptom_text = "Common symptoms include: " + ", ".join(common_symptoms[:10]) + "\n\n"
        return symptom_text + "What symptoms are you experiencing? Please list them separated by commas."

    @staticmethod
    def get_risk_factors_prompt(common_risk_factors: List[str]) -> str:
        risk_text = "Common risk factors include: " + ", ".join(common_risk_factors) + "\n\n"
        return (
            risk_text +
            "Do you have any known risk factors?\n"
            "Please list them separated by commas, or type 'None'."
        )