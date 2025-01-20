from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
)
from typing import Dict, Any, List
from diagnosis_calculator import DiagnosisCalculator
from message_formatter import MessageFormatter
from symptom_list import COMMON_SYMPTOMS
from risk_factors import COMMON_RISK_FACTORS
from diagnosis import POSSIBLE_DIAGNOSES
from health_chat_engine import HealthChatEngine

class HealthBot:
    # Define states for the conversation
    CHOOSING_MODE, AGE, SEX, SYMPTOMS, DURATION, SEVERITY, DRUG_HISTORY, TRAVEL_HISTORY, RISK_FACTORS, GENERAL_CHAT = range(10)

    # Predefined options
    DURATION_OPTIONS = [
        "Less than 24 hours",
        "1-3 days",
        "4-7 days",
        "1-2 weeks",
        "More than 2 weeks"
    ]
    
    SEVERITY_OPTIONS = [
        "1 - Very Mild",
        "2-3 - Mild",
        "4-5 - Moderate",
        "6-7 - Severe",
        "8-9 - Very Severe",
        "10 - Extremely Severe"
    ]
    
    DRUG_OPTIONS = [
        "No medications",
        "Over-the-counter pain relievers",
        "Prescription medications",
        "Multiple medications",
        "Other (please specify)"
    ]
    
    TRAVEL_OPTIONS = [
        "No recent travel",
        "Domestic travel",
        "International travel",
        "Multiple destinations",
        "Other (please specify)"
    ]
    
    RISK_FACTOR_OPTIONS = [
        "None",
        "High blood pressure",
        "Diabetes",
        "Heart disease",
        "Respiratory conditions",
        "Multiple conditions",
        "Other (please specify)"
    ]

    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.calculator = DiagnosisCalculator(POSSIBLE_DIAGNOSES)
        self.formatter = MessageFormatter()
        self.chat_engine = HealthChatEngine()  # Add this line


    def setup_handlers(self):
        """Setup all command and conversation handlers."""
        self.application.add_handler(self._setup_conversation())
        self.application.add_handler(CommandHandler("help", self._help))

    def run(self):
        """Start the bot."""
        print("Enhanced CareWave Bot is starting...")
        self.setup_handlers()
        self.application.run_polling()

    def _setup_conversation(self) -> ConversationHandler:
        """Set up the conversation handler with all states and transitions."""
        return ConversationHandler(
            entry_points=[CommandHandler("start", self._start)],
            states={
                self.CHOOSING_MODE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._choose_mode)
                ],
                self.AGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_age)
                ],
                self.SEX: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_sex)
                ],
                self.SYMPTOMS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_symptoms)
                ],
                self.DURATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_duration)
                ],
                self.SEVERITY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_severity)
                ],
                self.DRUG_HISTORY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_drug_history)
                ],
                self.TRAVEL_HISTORY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_travel_history)
                ],
                self.RISK_FACTORS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_risk_factors)
                ],
                self.GENERAL_CHAT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_general_chat)
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self._cancel),
                CommandHandler("start", self._start)
            ],
        )

    async def _start(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask for mode selection."""
        keyboard = [
            ["Health Assessment"],
            ["General Chat"],
            ["Health Information"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Welcome to CareWave! 👋 How can I help you today?",
            reply_markup=reply_markup
        )
        return self.CHOOSING_MODE

    async def _choose_mode(self, update: Update, context: CallbackContext) -> int:
        """Handle mode selection."""
        choice = update.message.text
        if choice == "Health Assessment":
            age_keyboard = [
                ["0-12", "13-19"],
                ["20-39", "40-59"],
                ["60-79", "80+"]
            ]
            reply_markup = ReplyKeyboardMarkup(age_keyboard, one_time_keyboard=True)
            await update.message.reply_text("Please select your age range:", reply_markup=reply_markup)
            return self.AGE
        elif choice == "General Chat":
            await update.message.reply_text(
                "I'm here to chat! Feel free to ask me anything about health, wellness, or general topics. "
                "You can return to the main menu anytime by typing /start",
                reply_markup=ReplyKeyboardRemove()
            )
            return self.GENERAL_CHAT
        elif choice == "Health Information":
            info_keyboard = [
                ["Common Symptoms", "Preventive Care"],
                ["First Aid", "Mental Health"],
                ["Back to Main Menu"]
            ]
            reply_markup = ReplyKeyboardMarkup(info_keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                "What would you like to learn about?",
                reply_markup=reply_markup
            )
            return self.GENERAL_CHAT
        else:
            await update.message.reply_text("Please select a valid option.")
            return self.CHOOSING_MODE

    async def _get_age(self, update: Update, context: CallbackContext) -> int:
        """Validate and collect user's age."""
        age_range = update.message.text
        context.user_data["age"] = age_range
        
        reply_markup = ReplyKeyboardMarkup([["Male", "Female", "Other"]], one_time_keyboard=True)
        await update.message.reply_text("What is your sex?", reply_markup=reply_markup)
        return self.SEX

    async def _get_sex(self, update: Update, context: CallbackContext) -> int:
        """Collect user's sex."""
        sex = update.message.text
        if sex not in ["Male", "Female", "Other"]:
            await update.message.reply_text("Please select a valid option: Male, Female, or Other")
            return self.SEX
        context.user_data["sex"] = sex
        
        # Create a keyboard with common symptoms
        symptom_keyboard = [[symptom] for symptom in COMMON_SYMPTOMS[:8]]  # Show first 8 symptoms
        symptom_keyboard.append(["Other symptoms"])
        reply_markup = ReplyKeyboardMarkup(symptom_keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "Please select your main symptom or type your symptoms:",
            reply_markup=reply_markup
        )
        return self.SYMPTOMS

    async def _get_symptoms(self, update: Update, context: CallbackContext) -> int:
        """Collect symptoms from the user."""
        symptoms = update.message.text
        if symptoms == "Other symptoms":
            await update.message.reply_text(
                "Please describe your symptoms in detail:",
                reply_markup=ReplyKeyboardRemove()
            )
            return self.SYMPTOMS
            
        context.user_data["symptoms"] = symptoms
        
        # Present duration options
        reply_markup = ReplyKeyboardMarkup(
            [[option] for option in self.DURATION_OPTIONS],
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "How long have you been experiencing these symptoms?",
            reply_markup=reply_markup
        )
        return self.DURATION

    async def _get_duration(self, update: Update, context: CallbackContext) -> int:
        """Collect duration of symptoms."""
        duration = update.message.text
        context.user_data["duration"] = duration
        
        reply_markup = ReplyKeyboardMarkup(
            [[option] for option in self.SEVERITY_OPTIONS],
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "How severe are your symptoms?",
            reply_markup=reply_markup
        )
        return self.SEVERITY

    async def _get_severity(self, update: Update, context: CallbackContext) -> int:
        """Collect symptom severity."""
        severity = update.message.text
        context.user_data["severity"] = severity

        reply_markup = ReplyKeyboardMarkup(
            [[option] for option in self.DRUG_OPTIONS],
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "Please select your medication status:",
            reply_markup=reply_markup
        )
        return self.DRUG_HISTORY

    async def _get_drug_history(self, update: Update, context: CallbackContext) -> int:
        """Collect drug history."""
        drug_history = update.message.text
        context.user_data["drug_history"] = drug_history
        
        reply_markup = ReplyKeyboardMarkup(
            [[option] for option in self.TRAVEL_OPTIONS],
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "Please select your recent travel history:",
            reply_markup=reply_markup
        )
        return self.TRAVEL_HISTORY

    async def _get_travel_history(self, update: Update, context: CallbackContext) -> int:
        """Collect travel history."""
        travel_history = update.message.text
        context.user_data["travel_history"] = travel_history
        
        reply_markup = ReplyKeyboardMarkup(
            [[option] for option in self.RISK_FACTOR_OPTIONS],
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "Do you have any of the following risk factors?",
            reply_markup=reply_markup
        )
        return self.RISK_FACTORS

    async def _get_risk_factors(self, update: Update, context: CallbackContext) -> int:
        """Collect risk factors and provide diagnosis."""
        risk_factors = update.message.text
        context.user_data["risk_factors"] = risk_factors if risk_factors.lower() != "none" else ""
        
        # Calculate diagnosis
        diagnosis_results = self.calculator.calculate_diagnosis(context.user_data)
        message = await MessageFormatter.format_diagnosis_result(diagnosis_results)
        
        await update.message.reply_text(message)
        await update.message.reply_text(
            "You can start a new assessment anytime by typing /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def _handle_general_chat(self, update: Update, context: CallbackContext) -> int:
        """Handle general conversation with the user."""
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        
        # Get response from chat engine (now non-async)
        response = self.chat_engine.process_message(user_id, user_message)
        
        await update.message.reply_text(response)
        return self.GENERAL_CHAT
    
    async def _cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancel the conversation."""
        await update.message.reply_text(
            "Operation cancelled. You can start again anytime by typing /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def _help(self, update: Update, context: CallbackContext) -> None:
        """Send help message with available commands."""
        help_text = (
            "🤖 CareWave Bot Help:\n\n"
            "Commands:\n"
            "🔹 /start - Start a new conversation or health assessment\n"
            "🔹 /cancel - Cancel current operation\n"
            "🔹 /help - Show this help message\n\n"
            "Features:\n"
            "🔸 Health Assessment\n"
            "🔸 General Health Information\n"
            "🔸 First Aid Tips\n"
            "🔸 Mental Health Resources\n\n"
            "Remember: This bot is not a replacement for professional medical care."
        )
        await update.message.reply_text(help_text)

def main():
    """Main function to run the bot."""
    bot = HealthBot("7846486562:AAEB3XHZWnj-5miT0OcFmKb_--WGQG26ir4")  # Replace with your actual bot token
    bot.run()

if __name__ == "__main__":
    main()