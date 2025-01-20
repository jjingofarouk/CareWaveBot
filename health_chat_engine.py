import random
import re
import asyncio
import logging
from typing import Dict, List, Tuple, Optional
import wikipedia
import spacy
import requests
from dataclasses import dataclass
from datetime import datetime
from fuzzywuzzy import fuzz
from collections import defaultdict

@dataclass
class ConversationContext:
    """Store conversation context and user preferences"""
    last_topic: Optional[str] = None
    conversation_history: List[Tuple[str, str]] = None
    user_preferences: Dict[str, any] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.user_preferences is None:
            self.user_preferences = {}

class HealthChatEngine:
    def __init__(self):
        # Load NLP model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize knowledge bases
        self.health_kb = self._initialize_health_knowledge()
        self.context_manager = self._initialize_context_manager()
        
        # Topic categories
        self.categories = {
            'general_health': ['wellness', 'lifestyle', 'nutrition', 'exercise', 'sleep'],
            'preventive_care': ['checkups', 'screenings', 'vaccinations', 'prevention'],
            'first_aid': ['emergency', 'wounds', 'burns', 'cpr', 'choking'],
            'mental_health': ['stress', 'anxiety', 'depression', 'mindfulness'],
            'conditions': ['symptoms', 'treatments', 'medications', 'chronic conditions']
        }
        
        # Response templates for more natural conversation
        self.response_templates = self._load_response_templates()
        
        # Conversation flow management
        self.conversation_states = defaultdict(lambda: {'context': ConversationContext()})



    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for various conversation scenarios"""
        return {
            'greeting': [
                "Hello! How can I help you with your health questions today? 👋",
                "Hi there! I'm here to discuss health and wellness with you. What's on your mind? 😊",
                "Welcome! I'd be happy to chat about health topics with you. What would you like to know? 🏥",
                "Greetings! I'm your health assistant. How may I help you today? 💪"
            ],
            'gratitude': [
                "You're welcome! Let me know if you have any other questions! 😊",
                "Glad I could help! Feel free to ask about other health topics! 👍",
                "Happy to assist! Your health is important! 💪",
                "It's my pleasure! Don't hesitate to ask if you need more information. 🌟"
            ],
            'farewell': [
                "Take care! Remember to prioritize your health! 👋",
                "Goodbye! Stay healthy and well! 💪",
                "Until next time! Take good care of yourself! 🌟",
                "Farewell! Remember, I'm here if you need health information! 😊"
            ],
            'emergency': [
                "🚨 Please seek immediate medical attention! This situation requires urgent care.",
                "🚨 This sounds serious. Please contact emergency services or visit the nearest emergency room.",
                "🚨 This requires immediate medical attention. Please call emergency services right away."
            ],
            'disclaimer': [
                "Remember, I'm here to provide general information only. Please consult healthcare professionals for medical advice.",
                "This information is for educational purposes. Always consult your healthcare provider for medical advice.",
                "While I can provide general information, please consult medical professionals for specific medical advice."
            ]
        }

    def process_message(self, user_id: str, message: str) -> str:
        """Process incoming message and generate appropriate response"""
        # Get user context
        context = self.conversation_states[user_id]['context']
        
        # Analyze message intent and entities
        intent, entities = self._analyze_message(message)
        
        # Update conversation context
        self._update_context(context, message, intent, entities)
        
        # Generate response based on intent and context
        response = self._generate_response(intent, entities, context)
        
        # Update conversation history
        context.conversation_history.append((message, response))
        if len(context.conversation_history) > 10:  # Keep last 10 exchanges
            context.conversation_history.pop(0)
            
        return response


    def _analyze_message(self, message: str) -> tuple[str, dict]:
        """Analyze message to determine intent and extract entities"""
        # Process message with spaCy
        doc = self.nlp(message.lower())
        
        # Extract entities
        entities = {ent.label_: ent.text for ent in doc.ents}
        
        # Determine intent
        intent = self._determine_intent(doc, message)
        
        return intent, entities

    def _generate_response(self, intent: str, entities: Dict, context: ConversationContext) -> str:
        """Generate appropriate response based on intent and context"""
        if intent == 'emergency':
            return self._generate_emergency_response(entities)
            
        elif intent == 'greeting':
            return self._generate_greeting(context)
            
        elif intent.startswith('info_request_'):
            category = intent.split('_')[-1]
            return self._generate_health_info(category, entities, context)
            
        elif intent == 'question':
            return self._generate_answer(entities, context)
            
        elif intent == 'gratitude':
            return self._generate_gratitude_response(context)
            
        return self._generate_general_chat_response(entities, context)

    def _generate_health_info(self, category: str, entities: Dict, context: ConversationContext) -> str:
        """Generate health information response based on category and entities"""
        # Try to get information from knowledge base first
        kb_info = self.health_kb.get(category, {})
        
        # If we have specific topic information
        if entities.get('TOPIC') and entities['TOPIC'] in kb_info:
            return self._format_response(kb_info[entities['TOPIC']], context)
        
        # Try to get information from Wikipedia for unknown topics
        try:
            if entities.get('TOPIC'):
                wiki_summary = wikipedia.summary(f"{entities['TOPIC']} health", sentences=2)
                return self._format_response(wiki_summary, context, include_disclaimer=True)
        except:
            pass
            
        # Fallback to general category information
        return self._format_response(kb_info.get('general', self._get_default_response(category)), context)


    def _determine_intent(self, doc, message: str) -> str:
        """Determine the user's intent from the message"""
        # Check for greeting patterns
        if any(token.text in ['hi', 'hello', 'hey'] for token in doc):
            return 'greeting'
            
        # Check for gratitude
        if any(token.text in ['thanks', 'thank', 'appreciate'] for token in doc):
            return 'gratitude'
            
        # Check for emergency keywords
        if any(word in message.lower() for word in ['emergency', 'urgent', 'help', '911']):
            return 'emergency'
            
        # Check for specific health topics
        for category, keywords in self.categories.items():
            if any(keyword in message.lower() for keyword in keywords):
                return f'info_request_{category}'
                
        # Check for question patterns
        if any(token.text in ['what', 'how', 'why', 'when', 'where'] for token in doc):
            return 'question'
            
        return 'general_chat'

    async def _generate_response(self, intent: str, entities: Dict, context: ConversationContext) -> str:
        """Generate appropriate response based on intent and context"""
        if intent == 'emergency':
            return self._generate_emergency_response(entities)
            
        elif intent == 'greeting':
            return self._generate_greeting(context)
            
        elif intent.startswith('info_request_'):
            category = intent.split('_')[-1]
            return await self._generate_health_info(category, entities, context)
            
        elif intent == 'question':
            return await self._generate_answer(entities, context)
            
        elif intent == 'gratitude':
            return self._generate_gratitude_response(context)
            
        return self._generate_general_chat_response(entities, context)

    async def _generate_health_info(self, category: str, entities: Dict, context: ConversationContext) -> str:
        """Generate health information response based on category and entities"""
        # Try to get information from knowledge base first
        kb_info = self.health_kb.get(category, {})
        
        # If we have specific topic information
        if entities.get('TOPIC') and entities['TOPIC'] in kb_info:
            return self._format_response(kb_info[entities['TOPIC']], context)
            
        # Try to get information from Wikipedia for unknown topics
        try:
            if entities.get('TOPIC'):
                wiki_summary = wikipedia.summary(f"{entities['TOPIC']} health", sentences=2)
                return self._format_response(wiki_summary, context, include_disclaimer=True)
        except:
            pass
            
        # Fallback to general category information
        return self._format_response(kb_info.get('general', self._get_default_response(category)), context)

    def _format_response(self, content: str, context: ConversationContext, include_disclaimer: bool = False) -> str:
        """Format response with appropriate conversational elements"""
        # Add conversation continuity elements
        if context.last_topic:
            content = self._add_topic_transition(context.last_topic, content)
            
        # Add engagement elements
        content = self._add_engagement_elements(content)
            
        # Add disclaimer if needed
        if include_disclaimer:
            content += "\n\nPlease consult healthcare professionals for medical advice."
            
        return content

    def _add_topic_transition(self, last_topic: str, content: str) -> str:
        """Add natural transition from previous topic"""
        transitions = {
            'general_health': "Speaking of general health, ",
            'preventive_care': "Related to prevention, ",
            'first_aid': "Regarding emergency care, ",
            'mental_health': "On the topic of mental well-being, "
        }
        
        transition = transitions.get(last_topic, "")
        return f"{transition}{content}" if transition else content

    def _add_engagement_elements(self, content: str) -> str:
        """Add conversational elements to make response more engaging"""
        # Add emojis where appropriate
        content = self._add_relevant_emojis(content)
        
        # Add conversation hooks
        hooks = [
            "Would you like to know more about this?",
            "Let me know if you have any questions!",
            "Is there anything specific you'd like me to explain further?"
        ]
        
        # Only add hooks sometimes to keep conversation natural
        if len(content.split()) > 30 and random.random() < 0.3:
            content += f"\n\n{random.choice(hooks)}"
            
        return content

    def _add_relevant_emojis(self, content: str) -> str:
        """Add relevant emojis to content"""
        emoji_map = {
            'exercise': '🏃‍♂️',
            'nutrition': '🥗',
            'sleep': '😴',
            'heart': '❤️',
            'emergency': '🚨',
            'mental health': '🧠',
            'medicine': '💊',
            'hospital': '🏥'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in content.lower():
                content = content.replace(keyword, f"{emoji} {keyword}")
                
        return content

    def _generate_emergency_response(self, entities: Dict) -> str:
        """Generate response for emergency situations"""
        return (
            "🚨 If you're experiencing a medical emergency, please:\n\n"
            "1. Call emergency services immediately (911 in the US)\n"
            "2. Don't wait for a bot response\n"
            "3. If possible, have someone stay with you until help arrives\n\n"
            "Remember: This bot is not a substitute for emergency medical care."
        )

    def _initialize_health_knowledge(self) -> Dict:
        """Initialize health knowledge base"""
        return {
            'general_health': {
                'general': (
                    "Maintaining good health involves several key factors:\n\n"
                    "1. Regular physical activity (150+ minutes/week)\n"
                    "2. Balanced nutrition\n"
                    "3. Adequate sleep (7-9 hours)\n"
                    "4. Stress management\n"
                    "5. Regular health check-ups"
                ),
                # Add more specific topics
            },
            'preventive_care': {
                'general': (
                    "Preventive care helps maintain health and catch issues early:\n\n"
                    "• Regular check-ups\n"
                    "• Health screenings\n"
                    "• Vaccinations\n"
                    "• Healthy lifestyle choices\n"
                    "• Regular exercise"
                ),
                # Add more specific topics
            },
            # Add other categories
        }

    def _initialize_context_manager(self):
        """Initialize conversation context manager"""
        return defaultdict(lambda: {
            'last_topic': None,
            'conversation_history': [],
            'user_preferences': {}
        })

    def _update_context(self, context: ConversationContext, message: str, intent: str, entities: Dict) -> None:
        """Update conversation context with new information"""
        # Update last topic if we have a topic-related intent
        if intent.startswith('info_request_'):
            context.last_topic = intent.split('_')[-1]
        
        # Update user preferences based on entities
        if entities:
            for entity_type, entity_value in entities.items():
                if entity_type not in ['DATE', 'TIME', 'CARDINAL']:  # Skip non-preference entities
                    context.user_preferences[entity_type] = entity_value

    def _generate_general_chat_response(self, entities: Dict, context: ConversationContext) -> str:
        """Generate response for general chat messages"""
        # If we have entities, try to provide relevant health information
        if entities:
            for entity_type, entity_value in entities.items():
                # Check if entity is related to any health categories
                for category, keywords in self.categories.items():
                    if any(keyword in entity_value.lower() for keyword in keywords):
                        return self._format_response(
                            self.health_kb.get(category, {}).get('general', 
                            f"I can provide information about {category.replace('_', ' ')}. What would you like to know?"),
                            context
                        )

        # If no specific health-related entities found, use generic responses
        generic_responses = [
            "I'm here to help with health-related questions. What would you like to know about?",
            "I can provide information about various health topics. Feel free to ask specific questions!",
            "I'm knowledgeable about health and wellness. What aspects interest you?",
            "Would you like to learn about any specific health topics? I can help with general health, preventive care, first aid, or mental health information."
        ]

        # Use conversation history to make response more contextual
        if context.conversation_history:
            last_exchange = context.conversation_history[-1]
            if any(keyword in last_exchange[0].lower() for keyword in ['thank', 'thanks']):
                return "You're welcome! What else would you like to know about?"
            
        return random.choice(generic_responses)
    
    def _generate_greeting(self, context: ConversationContext) -> str:
        """Generate a greeting response"""
        # Use the greeting templates we defined in _load_response_templates
        return random.choice(self.response_templates['greeting'])

def _generate_answer(self, entities: Dict, context: ConversationContext) -> str:
    """Generate an answer to a specific question"""
    # If we have entities, try to provide relevant information
    if entities:
        for entity_type, entity_value in entities.items():
            for category, keywords in self.categories.items():
                if any(keyword in entity_value.lower() for keyword in keywords):
                    return self._format_response(
                        self.health_kb.get(category, {}).get('general', 
                        f"I can provide information about {category.replace('_', ' ')}. What would you like to know?"),
                        context
                    )
    
    return "Could you please be more specific about what health-related information you're looking for?"

    def _generate_gratitude_response(self, context: ConversationContext) -> str:
        """Generate response to expressions of gratitude"""
        return random.choice(self.response_templates['gratitude'])

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for various conversation scenarios"""
        return {
            'greeting': [
                "Hello! How can I help you with your health questions today? 👋",
                "Hi there! I'm here to discuss health and wellness with you. What's on your mind? 😊",
                "Welcome! I'd be happy to chat about health topics with you. What would you like to know? 🏥"
            ],
            'gratitude': [
                "You're welcome! Let me know if you have any other questions! 😊",
                "Glad I could help! Feel free to ask about other health topics! 👍",
                "Happy to assist! Your health is important! 💪"
            ],
            # Add more template categories
        }

    def _get_default_response(self, category: str) -> str:
        """Get default response for a category when specific information isn't available"""
        defaults = {
            'general_health': "I can provide information about various health topics like nutrition, exercise, and wellness. What specifically would you like to know about?",
            'preventive_care': "Preventive care is crucial for maintaining good health. Would you like to learn about check-ups, screenings, or healthy lifestyle choices?",
            'first_aid': "I can provide basic first aid information. Please specify what type of situation you'd like to learn about.",
            'mental_health': "Mental health is as important as physical health. Would you like to discuss stress management, anxiety, or general mental wellness?",
            'conditions': "I can provide general information about various health conditions. What condition would you like to learn more about?"
        }
        return defaults.get(category, "I'd be happy to provide health information. What topic interests you?")

class WikipediaHealthAPI:
    """Helper class for fetching health-related information from Wikipedia"""
    
    def __init__(self):
        wikipedia.set_lang("en")
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour

    async def get_health_info(self, topic: str) -> Optional[str]:
        """Get health-related information about a topic"""
        try:
            # Try to get from cache first
            if topic in self.cache:
                timestamp, content = self.cache[topic]
                if (datetime.now() - timestamp).seconds < self.cache_timeout:
                    return content

            # Search Wikipedia
            search_term = f"{topic} health medical"
            page = wikipedia.page(search_term)
            
            # Extract relevant sections
            content = self._extract_relevant_sections(page)
            
            # Cache the result
            self.cache[topic] = (datetime.now(), content)
            
            return content
        except Exception as e:
            logging.error(f"Error fetching Wikipedia info: {str(e)}")
            return None

    def _extract_relevant_sections(self, page) -> str:
        """Extract relevant sections from Wikipedia page"""
        # Get the summary
        summary = page.summary
        
        # Look for health-related sections
        content = summary
        for section in ['Health', 'Medical', 'Treatment', 'Prevention']:
            try:
                section_content = page.section(section)
                if section_content:
                    content += f"\n\n{section}:\n{section_content}"
            except:
                continue
                
        return content[:1000]  # Limit length
    
    async def _generate_response(self, intent: str, entities: Dict, context: ConversationContext) -> str:
        """Generate appropriate response based on intent and context"""
        if intent == 'emergency':
            return self._generate_emergency_response(entities)
            
        elif intent == 'greeting':
            return self._generate_greeting(context)
            
        elif intent.startswith('info_request_'):
            category = intent.split('_')[-1]
            return await self._generate_health_info(category, entities, context)
            
        elif intent == 'question':
            return await self._generate_answer(entities, context)
            
        elif intent == 'gratitude':
            return self._generate_gratitude_response(context)
            
        return self._generate_general_chat_response(entities, context)

    def _generate_gratitude_response(self, context: ConversationContext) -> str:
        """Generate response to expressions of gratitude"""
        responses = [
            "You're welcome! Let me know if you have any other health-related questions.",
            "Happy to help! Feel free to ask about any other health topics.",
            "Glad I could assist! Is there anything else you'd like to know?"
        ]
        return random.choice(responses)

    def _generate_greeting(self, context: ConversationContext) -> str:
        """Generate greeting response"""
        return random.choice(self.response_templates['greeting'])    