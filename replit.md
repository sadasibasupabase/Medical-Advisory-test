# Overview

Medical Advisory Chatbot is a comprehensive Flask-based application that provides AI-powered medical triage and patient engagement services. The system integrates OpenAI's GPT models to offer symptom analysis, treatment summaries, clinical research capabilities, and patient care guidance while maintaining strict medical safety protocols and disclaimers.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Flask Framework**: Core web application framework with session management for user state
- **SQLAlchemy ORM**: Database abstraction layer with SQLite as the default database
- **Modular Design**: Clear separation between routes, models, and AI processing logic
- **Medical AI Module**: Dedicated module (`medical_ai.py`) for OpenAI integration with medical-specific prompting

## Frontend Architecture
- **Server-Side Rendered Templates**: Jinja2 templates with Bootstrap 5 dark theme
- **Progressive Enhancement**: Vanilla JavaScript for real-time chat functionality
- **Responsive Design**: Mobile-friendly interface with medical-themed styling
- **Component-Based UI**: Reusable base template with specialized pages for different functions

## Database Schema
- **User Management**: Role-based system supporting patients and healthcare providers
- **Conversation Tracking**: Complete chat history with model selection tracking
- **Medical Records**: Symptom logs with triage levels and treatment summaries
- **Research Repository**: Clinical paper storage and query capabilities
- **Reminder System**: Medication and appointment scheduling

## AI Integration Strategy
- **Model Selection**: Support for both GPT-4 and GPT-4o with user choice
- **Structured Responses**: JSON-formatted AI outputs for consistent data handling
- **Medical Guardrails**: Built-in safety prompts and disclaimer injection
- **Contextual Processing**: Specialized prompts for symptom analysis, research queries, and patient engagement

## Safety and Compliance
- **Medical Disclaimers**: Automatic injection on all medical responses
- **Triage Categories**: Three-tier system (urgent/monitor/mild) for symptom classification
- **Emergency Protocols**: Clear escalation paths for urgent medical situations
- **Professional Standards**: Maintains ethical guidelines for medical information systems

# External Dependencies

## AI Services
- **OpenAI API**: GPT-4 and GPT-4o models for natural language processing and medical analysis
- **API Key Management**: Environment variable-based configuration for secure API access

## Frontend Libraries
- **Bootstrap 5**: UI framework with Replit dark theme integration
- **Font Awesome**: Icon library for medical and interface symbols
- **Replit Agent Theme**: Custom dark theme optimized for the Replit environment

## Development Tools
- **Flask Development Server**: Built-in development server with debug mode
- **SQLite**: File-based database for development and small-scale deployment
- **Werkzeug ProxyFix**: Middleware for proper proxy header handling

## Session Management
- **Flask-Session**: Server-side session storage for chat history and user state
- **Cookie-Based Authentication**: Simple session management without complex auth flows

## Deployment Considerations
- **Environment Variables**: Configuration through environment variables for API keys and database URLs
- **Database Migration**: SQLAlchemy model-based table creation on startup
- **Static Asset Serving**: Flask's built-in static file serving for CSS and JavaScript