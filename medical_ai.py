import json
import os
import time
from dotenv import load_dotenv
from openai import AzureOpenAI
load_dotenv()

# Set your Azure OpenAI credentials
AZURE_OPENAI_VERSION= os.environ.get("AZURE_OPENAI_VERSION")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://abhij-meiln0rj-eastus2.cognitiveservices.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-5-mini")
subscription_key = os.getenv("AZURE_OPENAI_KEY")

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version=AZURE_OPENAI_VERSION,
)

model = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")

MEDICAL_DISCLAIMER = """

**IMPORTANT MEDICAL DISCLAIMER:** This is supportive information only, not medical advice. Please consult a licensed doctor for proper medical evaluation and treatment. In case of emergency, contact your local emergency services immediately."""

def analyze_symptoms(symptoms, model=model):
    print(f"Analyzing symptoms with model: {model}")
    """
    Analyze symptoms and provide triage-style response with medical guardrails
    """
    try:
       
        prompt = f"""
        You are a medical triage assistant. Analyze the following symptoms and provide a structured response.
        Please respond in JSON format with:
        {{
            "triage_level": "urgent|monitor|mild",
            "possible_conditions": ["condition1", "condition2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "red_flags": ["flag1", "flag2"] or [],
            "when_to_seek_care": "description"
        }}
        Guidelines:
        - Use "urgent" for symptoms requiring immediate medical attention
        - Use "monitor" for symptoms that need medical evaluation within 24-48 hours
        - Use "mild" for symptoms that can be self-monitored with routine care
        - Always err on the side of caution
        - Include red flags that would warrant immediate care
        """
        
        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": symptoms
                    }
                ]
            }
        ]
        
       # Include speech result if speech is enabled
        messages = chat_prompt

        start = time.time()
        print(f"Sending request to OpenAI API at {start}")
        # Generate the completion
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            # max_completion_tokens=800,
            stop=None,
            stream=False
        )

        end = time.time()
        print(f"Received response from OpenAI API in {end - start:.2f} seconds")

        # print(completion.to_json())
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Empty response from OpenAI API")
        result = json.loads(content)
        
        # Format response with disclaimer
        formatted_response = f"""
            **Symptom Analysis:**

            **Triage Level:** {result.get('triage_level', 'monitor').upper()}

            **Possible Conditions:**
            {chr(10).join([f"• {condition}" for condition in result.get('possible_conditions', [])])}

            **Recommendations:**
            {chr(10).join([f"• {rec}" for rec in result.get('recommendations', [])])}

            **When to Seek Care:** {result.get('when_to_seek_care', 'Consult a healthcare provider for proper evaluation')}
            """
        
        if result.get('red_flags'):
            formatted_response += f"""
                **⚠️ Red Flags - Seek Immediate Care:**
                {chr(10).join([f"• {flag}" for flag in result.get('red_flags', [])])}
                """
        
        formatted_response += MEDICAL_DISCLAIMER
        
        return {
            "response": formatted_response,
            "triage_level": result.get('triage_level', 'monitor'),
            "structured_data": result
        }

    except Exception as e:
        return {
            "response": f"I apologize, but I'm unable to analyze your symptoms right now due to a technical issue. Please consult a healthcare provider for medical advice.{MEDICAL_DISCLAIMER}",
            "triage_level": "monitor",
            "error": str(e)
        }

def generate_treatment_summary(discharge_notes, target_language="en", model=model):
    """
    Generate simplified treatment summaries in local languages
    """
    try:
        language_names = {
            "en": "English",
            "hi": "Hindi (हिंदी)"
        }
        
        prompt = f"""
        Convert the following medical discharge notes into a simplified, patient-friendly summary in {language_names.get(target_language, 'English')}.
        
        Discharge Notes: {discharge_notes}
        
        Create a clear, easy-to-understand summary that includes:
        1. What was treated
        2. Medications prescribed (with simple explanations)
        3. Follow-up care instructions
        4. Warning signs to watch for
        5. Lifestyle recommendations
        
        Use simple language that a patient can easily understand. If translating to Hindi, maintain medical accuracy while using common Hindi terms.
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a medical communication specialist. Create patient-friendly treatment summaries in {language_names.get(target_language, 'English')} that are accurate but easy to understand."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content or ""
        summary += MEDICAL_DISCLAIMER
        
        return summary
        
    except Exception as e:
        return f"Unable to generate treatment summary. Please consult your healthcare provider for clarification on your treatment plan.{MEDICAL_DISCLAIMER}"

# def research_query(query, research_papers_content, model="gpt-4o"):
def research_query(query, research_papers_content, model=model):
    """
    You are a clinical research analyst. Provide evidence-based answers with proper scientific rigor.
    Answer research queries by analyzing uploaded papers and creating evidence tables
    """
    try:
        prompt = f"""
        
        Research Papers Content:
        {research_papers_content[:8000]}  # Limit content to avoid token limits
        
        Please provide a structured response in JSON format:
        {{
            "summary": "Brief answer to the query",
            "evidence_table": [
                {{
                    "study_title": "title",
                    "sample_size": "number or description",
                    "key_outcome": "primary outcome measured",
                    "findings": "relevant findings",
                    "strength_of_evidence": "high/moderate/low"
                }}
            ],
            "clinical_implications": "What this means for clinical practice",
            "limitations": "Study limitations to consider"
        }}
        """
        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ]
        
       # Include speech result if speech is enabled
        messages = chat_prompt

        # Generate the completion
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            # max_completion_tokens=800,
            stop=None,
            stream=False
        )
        
        # response = client.chat.completions.create(
        #     model=model,
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a clinical research analyst. Provide evidence-based answers with proper scientific rigor."
        #         },
        #         {"role": "user", "content": prompt}
        #     ],
        #     # response_format={"type": "json_object"},
        #     temperature=0.2
        # )
        
        content = response.choices[0].message.content
        # print(response.to_json())
        if content is None:
            raise ValueError("Empty response from OpenAI API")
        result = json.loads(content)
        
        # Format the evidence table nicely
        formatted_response = f"""
**Research Summary:** {result.get('summary', '')}

**Evidence Table:**
"""
        
        for evidence in result.get('evidence_table', []):
            formatted_response += f"""
**Study:** {evidence.get('study_title', 'N/A')}
- **Sample Size:** {evidence.get('sample_size', 'N/A')}
- **Key Outcome:** {evidence.get('key_outcome', 'N/A')}
- **Findings:** {evidence.get('findings', 'N/A')}
- **Evidence Strength:** {evidence.get('strength_of_evidence', 'N/A')}
---
"""
        
        formatted_response += f"""
**Clinical Implications:** {result.get('clinical_implications', '')}

**Limitations:** {result.get('limitations', '')}
{MEDICAL_DISCLAIMER}
"""
        
        return formatted_response
        
    except Exception as e:
        return f"Unable to analyze research papers for your query. Please consult medical literature directly or speak with a healthcare provider.{MEDICAL_DISCLAIMER}"

def patient_engagement_response(message, context="general", model=model):
    """
    Provide conversational follow-ups, exercise guidance, and general patient support
    """
    try:
        # print(f"Generating patient engagement response with model: {model}")
        system_prompts = {
            "exercise": "You are a rehabilitation specialist providing safe, general exercise guidance. Always recommend consulting healthcare providers for personalized plans.",
            "followup": "You are a patient care coordinator providing supportive follow-up guidance and encouragement.",
            "general": "You are a supportive healthcare assistant providing general wellness information and encouragement."
        }

        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompts.get(context, system_prompts["general"])
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
        
       # Include speech result if speech is enabled
        messages = chat_prompt

        start = time.time()
        print(f"Sending request to OpenAI API at {start}")

        # Generate the completion
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            # max_completion_tokens=800,
            stop=None,
            stream=False
        )

        end = time.time()
        print(f"Received response from OpenAI API in {end - start:.2f} seconds")
        
        response_text = response.choices[0].message.content or ""
        
        # Add disclaimer for medical-related responses
        if any(term in message.lower() for term in ['pain', 'medication', 'exercise', 'therapy', 'treatment', 'symptom']):
            response_text += MEDICAL_DISCLAIMER
            
        return response_text
        
    except Exception as e:
        return f"I'm unable to provide guidance right now. Please consult your healthcare provider for personalized advice.{MEDICAL_DISCLAIMER}"
