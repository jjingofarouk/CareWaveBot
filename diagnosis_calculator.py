from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

class DiagnosisCalculator:
    def __init__(self, possible_diagnoses: List[Dict[str, Any]]):
        """
        Initialize the DiagnosisCalculator with possible diagnoses.
        
        Args:
            possible_diagnoses: List of dictionaries containing diagnosis information
        """
        if not isinstance(possible_diagnoses, list):
            raise ValueError("possible_diagnoses must be a list")
        self.possible_diagnoses = possible_diagnoses
        self.symptom_weights = {
            'primary': 0.5,
            'secondary': 0.3,
            'tertiary': 0.2
        }

    def calculate_diagnosis(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate diagnosis based on user inputs.
        
        Args:
            user_data: Dictionary containing user health information
            
        Returns:
            List of dictionaries containing diagnosis results
        """
        try:
            # Input validation
            if not isinstance(user_data, dict):
                raise ValueError("user_data must be a dictionary")

            # Parse and normalize user inputs with defaults
            user_symptoms = self._normalize_symptoms(user_data.get('symptoms', ''))
            user_risk_factors = self._normalize_list(user_data.get('risk_factors', ''))
            severity = self._parse_severity(user_data.get('severity', 'moderate'))
            age = self._parse_age_range(user_data.get('age', 'adult'))
            duration = self._parse_duration(user_data.get('duration', '1-3 days'))
            
            results = []
            
            for diagnosis in self.possible_diagnoses:
                score = self._calculate_comprehensive_score(
                    diagnosis=diagnosis,
                    user_symptoms=user_symptoms,
                    user_risk_factors=user_risk_factors,
                    severity=severity,
                    age=age,
                    duration=duration,
                    sex=user_data.get('sex', ''),
                    drug_history=user_data.get('drug_history', ''),
                    travel_history=user_data.get('travel_history', '')
                )
                
                matching_factors = self._analyze_matching_factors(
                    diagnosis=diagnosis,
                    user_data={
                        'symptoms': user_symptoms,
                        'risk_factors': user_risk_factors,
                        'travel_history': user_data.get('travel_history', ''),
                        'drug_history': user_data.get('drug_history', '')
                    }
                )
                
                results.append({
                    "diagnosis": diagnosis.get('diagnosis', 'Unknown'),
                    "probability": round(score, 2),
                    "confidence": self._calculate_confidence_level(score, matching_factors),
                    "matching_factors": matching_factors,
                    "recommendations": self._generate_recommendations(diagnosis, score, matching_factors)
                })

            return self._apply_differential_diagnosis(results)
            
        except Exception as e:
            print(f"Error in calculate_diagnosis: {str(e)}")
            return [{"diagnosis": "Error", "probability": 0, "confidence": {"level": "Low", "score": 0}}]

    def _parse_severity(self, severity: str) -> float:
        """Parse severity string to float value."""
        try:
            severity_mapping = {
                "mild": 0.3,
                "moderate": 0.6,
                "severe": 1.0,
                "1 - very mild": 0.1,
                "2-3 - mild": 0.3,
                "4-5 - moderate": 0.5,
                "6-7 - severe": 0.7,
                "8-9 - very severe": 0.9,
                "10 - extremely severe": 1.0
            }
            return severity_mapping.get(severity.lower(), 0.5)
        except Exception:
            return 0.5

    def _parse_age_range(self, age: Union[str, int]) -> str:
        """Parse age input to age category."""
        try:
            # Handle string age ranges
            if isinstance(age, str):
                age_range_mapping = {
                    "0-12": "Child",
                    "13-19": "Young Adult",
                    "20-39": "Young Adult",
                    "40-59": "Adult",
                    "60-79": "Senior",
                    "80+": "Senior"
                }
                return age_range_mapping.get(age, "Adult")
            
            # Handle numeric age
            numeric_age = int(age)
            if numeric_age < 13:
                return "Child"
            elif 13 <= numeric_age < 40:
                return "Young Adult"
            elif 40 <= numeric_age < 60:
                return "Adult"
            else:
                return "Senior"
                
        except (ValueError, TypeError):
            return "Adult"

    def _parse_duration(self, duration: str) -> int:
        """Convert duration string to days."""
        try:
            duration_mapping = {
                "less than 24 hours": 1,
                "1-3 days": 2,
                "4-7 days": 5,
                "1-2 weeks": 10,
                "more than 2 weeks": 15
            }
            return duration_mapping.get(duration.lower(), 2)
        except Exception:
            return 2

    def _calculate_risk_score(
        self,
        user_risk_factors: List[str],
        diagnosis_risk_factors: List[str],
        risk_weights: Dict[str, float]
    ) -> float:
        """Calculate risk score based on matching risk factors."""
        try:
            if not diagnosis_risk_factors:
                return 0.0
                
            matches = sum(1 for risk in user_risk_factors if risk in diagnosis_risk_factors)
            base_score = (matches / len(diagnosis_risk_factors)) * 100
            
            # Apply weights if available
            if risk_weights:
                weighted_score = 0
                for risk in user_risk_factors:
                    if risk in diagnosis_risk_factors:
                        weighted_score += risk_weights.get(risk, 1.0)
                return min(weighted_score * 20, 100)  # Scale to 0-100
                
            return base_score
            
        except Exception:
            return 0.0

    def _calculate_comprehensive_score(
        self,
        diagnosis: Dict[str, Any],
        user_symptoms: List[str],
        user_risk_factors: List[str],
        severity: float,
        age: str,
        duration: int,
        sex: str,
        drug_history: str,
        travel_history: str
    ) -> float:
        """Calculate comprehensive diagnosis score."""
        try:
            score = 0.0
            
            # Symptom score (40%)
            symptom_score = self._calculate_weighted_symptom_score(
                user_symptoms, 
                diagnosis.get('symptoms', {}),
                diagnosis.get('symptom_weights', self.symptom_weights)
            )
            score += symptom_score * 0.4
            
            # Risk score (20%)
            risk_score = self._calculate_risk_score(
                user_risk_factors,
                diagnosis.get('risk_factors', []),
                diagnosis.get('risk_weights', {})
            )
            score += risk_score * 0.2
            
            # Severity score (15%)
            severity_score = self._calculate_severity_alignment(
                severity,
                diagnosis.get('typical_severity', 0.5)
            )
            score += severity_score * 0.15
            
            # Age appropriateness (10%)
            age_score = self._calculate_age_appropriateness(
                age,
                diagnosis.get('age_range', []),
                diagnosis.get('age_risk_factors', {})
            )
            score += age_score * 0.1
            
            # Duration appropriateness (10%)
            duration_score = self._calculate_duration_appropriateness(
                duration,
                diagnosis.get('typical_duration', {}),
                diagnosis.get('duration_weights', {})
            )
            score += duration_score * 0.1
            
            # Contextual factors (5%)
            context_score = self._evaluate_contextual_factors(
                diagnosis,
                {'sex': sex, 'drug_history': drug_history, 'travel_history': travel_history}
            )
            score += context_score * 0.05
            
            return min(max(score, 0.0), 100.0)
            
        except Exception as e:
            print(f"Error in comprehensive score calculation: {str(e)}")
            return 0.0

    def _calculate_weighted_symptom_score(
        self,
        user_symptoms: List[str],
        diagnosis_symptoms: Dict[str, List[str]],
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted symptom score."""
        try:
            score = 0.0
            total_weight = 0.0
            
            for category, weight in weights.items():
                if category in diagnosis_symptoms:
                    matches = len([s for s in user_symptoms if s in diagnosis_symptoms[category]])
                    total_possible = len(diagnosis_symptoms[category])
                    if total_possible > 0:
                        score += (matches / total_possible) * weight
                        total_weight += weight
            
            return (score / total_weight * 100) if total_weight > 0 else 0
            
        except Exception:
            return 0.0

    def _calculate_severity_alignment(self, user_severity: float, typical_severity: float) -> float:
        """Calculate how well the user's severity aligns with typical severity."""
        try:
            difference = abs(user_severity - typical_severity)
            return max(100 - (difference * 100), 0)
        except Exception:
            return 0.0

    def _calculate_age_appropriateness(
        self,
        age: str,
        age_ranges: List[str],
        age_risk_factors: Dict[str, float]
    ) -> float:
        """Calculate age appropriateness score."""
        try:
            if not age_ranges:
                return 100.0
            
            if age in age_ranges:
                base_score = 100.0
            else:
                base_score = 50.0
            
            # Apply age-specific risk factors
            risk_modifier = age_risk_factors.get(age, 1.0)
            return base_score * risk_modifier
            
        except Exception:
            return 50.0

    def _calculate_duration_appropriateness(
        self,
        duration: int,
        typical_duration: Dict[str, int],
        duration_weights: Dict[str, float]
    ) -> float:
        """Calculate duration appropriateness score."""
        try:
            if not typical_duration:
                return 100.0
            
            min_duration = typical_duration.get('min', 0)
            max_duration = typical_duration.get('max', float('inf'))
            
            if min_duration <= duration <= max_duration:
                return 100.0
            
            # Calculate penalty for duration mismatch
            if duration < min_duration:
                penalty = (min_duration - duration) / min_duration
            else:
                penalty = (duration - max_duration) / max_duration
                
            return max(100 - (penalty * 50), 0)
            
        except Exception:
            return 50.0

    def _evaluate_contextual_factors(
        self,
        diagnosis: Dict[str, Any],
        context: Dict[str, str]
    ) -> float:
        """Evaluate contextual factors for diagnosis."""
        try:
            score = 100.0
            relevant_factors = 0
            
            # Check sex-specific conditions
            if diagnosis.get('sex_specific'):
                if context['sex'].lower() != diagnosis['sex_specific'].lower():
                    score *= 0.5
                relevant_factors += 1
            
            # Check drug interactions
            if diagnosis.get('drug_interactions'):
                if any(drug in context['drug_history'].lower() 
                      for drug in diagnosis['drug_interactions']):
                    score *= 0.7
                relevant_factors += 1
            
            # Check travel-related factors
            if diagnosis.get('travel_related'):
                if 'no recent travel' in context['travel_history'].lower():
                    score *= 0.8
                relevant_factors += 1
            
            return score if relevant_factors > 0 else 100.0
            
        except Exception:
            return 50.0

    def _analyze_matching_factors(
        self,
        diagnosis: Dict[str, Any],
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze matching factors between user data and diagnosis."""
        try:
            # Combine primary and secondary symptoms into a single list
            matching_symptoms = [
                symptom for symptom in user_data['symptoms']
                if (symptom in diagnosis.get('symptoms', {}).get('primary', []) or
                    symptom in diagnosis.get('symptoms', {}).get('secondary', []))
            ]
            
            # Get matching risk factors
            matching_risk_factors = [
                factor for factor in user_data['risk_factors']
                if factor in diagnosis.get('risk_factors', [])
            ]

            # Check travel risk
            travel_match = ('No' if not diagnosis.get('travel_related') or
                        'no recent travel' in user_data['travel_history'].lower()
                        else user_data['travel_history'])

            return {
                "symptom_match": matching_symptoms,
                "risk_factor_match": matching_risk_factors,
                "travel_risk_match": travel_match
            }
        except Exception:
            return {
                "symptom_match": [],
                "risk_factor_match": [],
                "travel_risk_match": "No"
            }
        
    def _calculate_confidence_level(
        self,
        probability: float,
        matching_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate confidence level for diagnosis."""
        try:
            # Base confidence calculation
            confidence_score = min(
                100,
                probability * 0.7 +
                (len(matching_factors['primary_symptoms']) * 10) +
                (len(matching_factors['risk_factors']) * 5)
            )
            
            # Determine confidence level
            if confidence_score >= 75:
                level = "High"
            elif confidence_score >= 50:
                level = "Medium"
            else:
                level = "Low"
            
            # Calculate confidence interval
            margin_of_error = (100 - confidence_score) * 0.2
            confidence_interval = (
                max(0, probability - margin_of_error),
                min(100, probability + margin_of_error)
            )
            
            return {
                "level": level,
                "score": round(confidence_score, 2),
                "interval": [round(x, 2) for x in confidence_interval],
                "factors": self._analyze_confidence_factors(matching_factors)
            }
            
        except Exception:
            return {
                "level": "Low",
                "score": 0.0,
                "interval": [0.0, 0.0],
                "factors": []
            }

    def _analyze_confidence_factors(self, matching_factors: Dict[str, Any]) -> List[str]:
            """Analyze factors contributing to confidence level."""
            try:
                factors = []
                if matching_factors['primary_symptoms']:
                    factors.append("Strong primary symptom correlation")
                if matching_factors['risk_factors']:
                    factors.append("Relevant risk factors present")
                if matching_factors.get('travel_risk_match'):
                    factors.append("Travel history aligns with diagnosis")
                if matching_factors['secondary_symptoms']:
                    factors.append("Supporting secondary symptoms present")
                if len(matching_factors['primary_symptoms']) >= 2:
                    factors.append("Multiple primary symptoms detected")
                return factors
                
            except Exception:
                return []

    def _generate_recommendations(
        self,
        diagnosis: Dict[str, Any],
        probability: float,
        matching_factors: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on diagnosis results."""
        try:
            recommendations = []
            
            # High probability recommendations
            if probability >= 75:
                if diagnosis.get('urgent_care_needed', False):
                    recommendations.append("Seek immediate medical attention")
                recommendations.extend(diagnosis.get('primary_recommendations', []))
                
            # Medium probability recommendations
            elif probability >= 50:
                recommendations.append("Consider consulting a healthcare provider")
                recommendations.extend(diagnosis.get('secondary_recommendations', []))
                
            # Low probability recommendations
            else:
                recommendations.append("Monitor symptoms for changes")
                recommendations.extend(diagnosis.get('general_recommendations', []))
            
            # Add risk factor specific recommendations
            if matching_factors['risk_factors']:
                recommendations.extend(self._get_risk_factor_recommendations(
                    diagnosis,
                    matching_factors['risk_factors']
                ))
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception:
            return ["Please consult a healthcare provider for accurate diagnosis"]

    def _get_risk_factor_recommendations(
        self,
        diagnosis: Dict[str, Any],
        risk_factors: List[str]
    ) -> List[str]:
        """Get recommendations specific to identified risk factors."""
        try:
            recommendations = []
            risk_recommendations = diagnosis.get('risk_factor_recommendations', {})
            
            for risk_factor in risk_factors:
                if risk_factor in risk_recommendations:
                    recommendations.extend(risk_recommendations[risk_factor])
            
            return recommendations
            
        except Exception:
            return []

    def _apply_differential_diagnosis(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply differential diagnosis logic to results."""
        try:
            # Sort by probability
            sorted_results = sorted(
                results,
                key=lambda x: (x['probability'], x['confidence']['score']),
                reverse=True
            )
            
            # Filter out very low probability diagnoses
            filtered_results = [
                result for result in sorted_results
                if result['probability'] >= 10.0
            ]
            
            # Adjust confidence levels for similar diagnoses
            return self._adjust_similar_diagnoses(filtered_results)
            
        except Exception:
            return results

    def _adjust_similar_diagnoses(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Adjust confidence levels for similar diagnoses."""
        try:
            if not results:
                return results
                
            adjusted_results = results.copy()
            top_diagnosis = results[0]
            
            for i, diagnosis in enumerate(adjusted_results[1:], 1):
                # Check for overlapping symptoms
                similarity_score = self._calculate_similarity(
                    top_diagnosis['matching_factors'],
                    diagnosis['matching_factors']
                )
                
                # Adjust confidence if diagnoses are very similar
                if similarity_score > 0.7:
                    adjusted_results[i]['confidence']['level'] = "Medium"
                    adjusted_results[i]['confidence']['score'] *= 0.9
                    
            return adjusted_results
            
        except Exception:
            return results

    def _calculate_similarity(
        self,
        factors1: Dict[str, Any],
        factors2: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two sets of matching factors."""
        try:
            primary_intersection = len(
                set(factors1['primary_symptoms']) &
                set(factors2['primary_symptoms'])
            )
            secondary_intersection = len(
                set(factors1['secondary_symptoms']) &
                set(factors2['secondary_symptoms'])
            )
            risk_intersection = len(
                set(factors1['risk_factors']) &
                set(factors2['risk_factors'])
            )
            
            total_factors = len(factors1['primary_symptoms']) + \
                          len(factors1['secondary_symptoms']) + \
                          len(factors1['risk_factors'])
            
            if total_factors == 0:
                return 0.0
                
            return (primary_intersection * 0.5 + 
                   secondary_intersection * 0.3 +
                   risk_intersection * 0.2) / total_factors
                   
        except Exception:
            return 0.0

    def _normalize_symptoms(self, symptoms: Union[str, List[str]]) -> List[str]:
        """Normalize symptom input to list format."""
        try:
            if isinstance(symptoms, list):
                return [s.lower().strip() for s in symptoms if s]
            elif isinstance(symptoms, str):
                return [s.lower().strip() for s in symptoms.split(',') if s]
            return []
        except Exception:
            return []

    def _normalize_list(self, items: Union[str, List[str]]) -> List[str]:
        """Normalize any list input to standard format."""
        try:
            if isinstance(items, list):
                return [i.lower().strip() for i in items if i]
            elif isinstance(items, str):
                return [i.lower().strip() for i in items.split(',') if i]
            return []
        except Exception:
            return []