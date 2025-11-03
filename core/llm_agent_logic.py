import os
import json
import sys
import time
from typing import List, Dict, Any

# =============================================
# CRITICAL FIX: Add parent directory to Python path
# =============================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment from project root
from dotenv import load_dotenv
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path, override=True)

print(f"🔧 llm_agent_logic - Current directory: {current_dir}")

# Debug environment
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY NOT FOUND!")

# --- LangChain RAG & Core Imports ---
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

# --- LangChain Gemini Integration ---
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage

# --- Configuration ---
VECTOR_DB_PATH = "AI-Powered-Citizen-Service-Chatbot/faiss_index" 
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 
VECTOR_DB = None
GEMINI_LLM = None
LLM_INITIALIZED = False

# --- ENHANCED ROBUST LLM Prompt Guidelines ---
LLM_PROMPT_GUIDELINES = {
    "QUERY_UNDERSTANDING": (
        "COMPREHENSIVE QUERY ANALYSIS AGENT - OUTPUT ONLY JSON:\n"
        "DEEP ANALYSIS: Examine the user query for:\n"
        "1. Primary service category: aadhar, pan, passport, general_govt_service\n"
        "2. Query type: information_request, procedure_help, document_requirements, eligibility, application_process\n"
        "3. Required action: respond, form_assistance, location_service, clarification\n"
        "4. Complexity level: simple_fact, multi_step_process, comparative_analysis\n"
        "5. User intent: immediate_help, detailed_guidance, location_finding\n\n"
        
        "OUTPUT FORMAT (STRICT JSON):\n"
        "{\n"
        "  \"intent\": \"information_request|procedure_help|document_help\",\n"
        "  \"topic\": \"aadhar|pan|passport|general\",\n"
        "  \"action_required\": \"respond|form_assistance|location_service|ask_clarification\",\n"
        "  \"complexity\": \"simple|detailed\",\n"
        "  \"focus_areas\": [\"array\", \"of\", \"specific\", \"aspects\"]\n"
        "}\n\n"
        
        "FORM_ASSISTANCE DETECTION: Use form_assistance for queries about 'form', 'fill', 'field', 'application form', 'documentation', 'submit', 'apply', 'online form'\n"
        "LOCATION_SERVICE DETECTION: Use location_service for queries about 'where', 'location', 'center', 'office', 'near me', 'address', 'find', 'locate', 'nearest'\n"
        
        "SEARCH STRATEGY: Identify multiple relevant angles to search in documents.\n"
        "BE THOROUGH: Consider all possible interpretations of the query."
    ),
    "DOCUMENT_RETRIEVAL": (
        "COMPREHENSIVE KNOWLEDGE RETRIEVAL AGENT:\n"
        "SEARCH STRATEGY:\n"
        "1. Perform BROAD semantic search across entire document database\n"
        "2. Retrieve 8-10 most relevant chunks for comprehensive coverage\n"
        "3. Include documents that cover:\n"
        "   - Direct answers to the query\n"
        "   - Related procedures and requirements\n"
        "   - Common scenarios and edge cases\n"
        "   - Step-by-step processes\n"
        "   - Official guidelines and rules\n"
        "4. Use multiple search strategies:\n"
        "   - Primary query search\n"
        "   - Focus area specific searches\n"
        "   - Related concept expansion\n\n"
        
        "RETRIEVAL RULES:\n"
        "- Prioritize completeness and quality over speed\n"
        "- Include multiple perspectives from different documents\n"
        "- Capture both general guidelines and specific details\n"
        "- Return ALL relevant information chunks\n"
        "- Ensure coverage of all aspects mentioned in query analysis"
    ),
    "SUMMARIZATION": (
        "EXPERT CITIZEN SERVICE CONSULTANT - COMPREHENSIVE RESPONSE:\n"
        "RESPONSE PHILOSOPHY: Provide ChatGPT-like detailed, helpful, and natural responses that cover all aspects of the query while being concise and structured.\n\n"
        
        "RESPONSE STRUCTURE RULES:\n"
        "1. OPENING: Start with 'I'll help you with that. Based on available information:'\n"
        "2. CONTENT: Provide 5-6 comprehensive bullet points covering different aspects using • format\n"
        "3. DEPTH: Each point should be 15-25 words - sufficiently detailed but concise\n"
        "4. COVERAGE: Ensure all identified focus areas from query analysis are addressed\n"
        "5. FLOW: Maintain natural, conversational language like a helpful assistant\n"
        "6. COMPLETENESS: Answer should stand alone as complete information\n\n"
        
        "CONTENT GUIDELINES:\n"
        "- Base answers STRICTLY on retrieved document context\n"
        "- If context is insufficient, provide helpful fallback information\n"
        "- Connect related concepts for better understanding\n"
        "- Include practical tips and important considerations\n"
        "- Mention documentation requirements when relevant\n"
        "- Highlight critical steps or common mistakes\n"
        "- Provide actionable information users can immediately use\n"
        "- ALWAYS use bullet points (•) for better readability\n\n"
        
        "FORMAT EXAMPLE:\n"
        "I'll help you with that. Based on available information:\n\n"
        "• [Detailed point 1 covering one aspect with practical details]\n"
        "• [Detailed point 2 covering another important angle]\n"
        "• [Point 3 with relevant requirements or considerations]\n"
        "• [Point 4 mentioning documentation or procedures]\n"
        "• [Point 5 with additional helpful information or tips]\n"
        "• [Point 6 covering any remaining important aspects]\n\n"
        
        "TEMPERATURE: 0.3 - Maintain accuracy while being naturally helpful"
    ),
    "ACTION_PLANNING": (
        "INTELLIGENT WORKFLOW ORCHESTRATOR:\n"
        "COMPREHENSIVE DECISION MATRIX:\n"
        "\n"
        "FORM_ASSISTANCE triggers when:\n"
        "- Query contains: 'form', 'fill', 'field', 'application form', 'documentation', 'submit', 'apply', 'online form'\n"
        "- User asks about: specific form fields, form steps, form requirements\n"
        "- Context involves: application procedures, submission processes\n"
        "\n"
        "LOCATION_SERVICE triggers when:\n"
        "- Query contains: 'where', 'location', 'center', 'office', 'near me', 'address', 'find', 'locate', 'nearest'\n"
        "- User asks about: service centers, offices, physical locations\n"
        "- Context involves: visiting centers, in-person services\n"
        "\n"
        "ASK_CLARIFICATION triggers when:\n"
        "- Topic is 'general' AND intent is unclear\n"
        "- Multiple services could be relevant\n"
        "- Query is too vague for specific action\n"
        "\n"
        "RESPOND triggers for:\n"
        "- All information requests, procedures, document queries\n"
        "- Application processes and requirements\n"
        "- General government service information\n"
        "\n"
        "OUTPUT FORMAT:\n"
        "{\n"
        "  \"action\": \"chosen_action\",\n"
        "  \"message\": \"Detailed reasoning for action selection\",\n"
        "  \"confidence\": \"high|medium|low\",\n"
        "  \"next_steps\": [\"array\", \"of\", \"suggested\", \"actions\"]\n"
        "}"
    ),
    "LOCATION_SERVICE": (
        "HELPFUL LOCATION FACILITATOR - NATURAL RESPONSE:\n"
        "RESPONSE APPROACH: Be genuinely helpful and guide users effectively\n\n"
        "RESPONSE STRUCTURE:\n"
        "1. EMPATHETIC ACKNOWLEDGMENT: Show understanding of their location need\n"
        "2. CLEAR ACTION REQUEST: Politely ask for specific location information\n"
        "3. VALUE EXPLANATION: Briefly explain how this helps provide better service\n"
        "4. ADDITIONAL SUPPORT: Offer alternative help if location isn't available\n\n"
        "EXAMPLE RESPONSES:\n"
        "\"I'd be happy to help you find the nearest Aadhaar enrollment centers! To give you the most accurate locations, could you please share your city name or postal code? This helps me filter for centers closest to your area.\"\n\n"
        "\"I can assist you in locating Aadhaar service centers for your needs. Please provide your city or area name so I can find the most convenient options for you. If you're not comfortable sharing location details, I can also guide you on how to find centers through the official UIDAI website.\"\n\n"
        "KEY POINTS:\n"
        "- Sound genuinely helpful and patient\n"
        "- Explain why location information improves service\n"
        "- Offer alternatives if user prefers not to share location\n"
        "- Keep tone warm and supportive"
    ),
    "FORM_ASSISTANCE": (
        "DETAILED FORM GUIDANCE EXPERT - COMPREHENSIVE HELP:\n"
        "RESPONSE PHILOSOPHY: Provide thorough, step-by-step form assistance that anticipates user needs and potential questions.\n\n"
        "RESPONSE STRUCTURE:\n"
        "1. INTRODUCTION: Acknowledge the form assistance request specifically\n"
        "2. COMPREHENSIVE STEPS: 5-6 detailed, numbered steps covering the entire process\n"
        "3. DOCUMENTATION: Clearly list required documents with specifics\n"
        "4. IMPORTANT NOTES: Highlight critical information, deadlines, special requirements\n"
        "5. TROUBLESHOOTING: Mention common issues and how to avoid them\n\n"
        "CONTENT GUIDELINES:\n"
        "- Each step should be 15-25 words - sufficiently detailed\n"
        "- Include both online and offline procedures if relevant\n"
        "- Mention where to find forms and submission venues\n"
        "- Specify processing times and follow-up procedures\n"
        "- Include verification and tracking information\n"
        "- Cover the entire process from start to completion\n"
        "- Use bullet points (•) for better readability\n\n"
        "FORMAT EXAMPLE:\n"
        "I'll provide detailed guidance for the Aadhaar form process:\n\n"
        "1. [Detailed step one with specific actions and locations]\n"
        "2. [Step two with documentation requirements and procedures]\n"
        "3. [Step three covering submission and verification]\n"
        "4. [Step four with follow-up actions and tracking]\n"
        "5. [Step five about collection and activation]\n"
        "6. [Important notes about processing times and requirements]\n\n"
        "Required documents: [Specific document list with details]\n\n"
        "Additional tips: [Helpful information for smooth processing]\n\n"
        "BE THOROUGH: Cover all aspects of form filling from start to completion"
    )
}

def initialize_llm():
    """Initialize Gemini with temperature 0.3 for more natural responses"""
    global GEMINI_LLM, LLM_INITIALIZED
    
    # Force reload environment variables
    load_dotenv(env_path, override=True)
    
    try:
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        
        print(f"🔑 DEBUG: Looking for GEMINI_API_KEY...")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set or empty.")
        
        # Check for placeholder patterns
        placeholder_indicators = ["your_", "paste_", "example", "replace", "xxxx", "actual_key"]
        if any(indicator in api_key.lower() for indicator in placeholder_indicators):
            raise ValueError("The GEMINI_API_KEY appears to be a placeholder value.")
        
        print(f"✅ Found API key (first 10 chars): {api_key[:10]}...")
        
        # Configure Gemini directly
        try:
            print("🔄 Configuring Gemini with google.generativeai...")
            genai.configure(api_key=api_key)
            
            # Test direct configuration
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Say OK if working")
            print(f"✅ Direct Gemini test: {response.text}")
        except Exception as direct_error:
            print(f"⚠️ Direct config failed: {direct_error}")
        
        # Available models - prioritize comprehensive models
        available_models = [
            "models/gemini-2.5-flash",     # Primary - comprehensive
            "gemini-1.5-flash-latest",     # Alternative
            "models/gemini-2.5-pro",       # More detailed responses
            "gemini-1.0-pro",              # Fallback
            "gemini-pro"                   # Most compatible
        ]
        
        successful_model = None
        
        for model_name in available_models:
            try:
                print(f"🔄 Trying model: {model_name}")
                
                # Initialize with temperature 0.3 for more natural responses
                GEMINI_LLM = ChatGoogleGenerativeAI(
                    model=model_name, 
                    temperature=0.3,  # Changed from 0.1 to 0.3
                    google_api_key=api_key,
                    max_retries=2,
                    timeout=60,  # Increased timeout
                    max_output_tokens=1000,  # Increased for more detailed responses
                )
                
                # Quick test with simple message
                test_response = GEMINI_LLM.invoke([HumanMessage(content="Say OK if working")])
                print(f"✅ Model {model_name} working: {test_response.content}")
                successful_model = model_name
                break
                
            except Exception as model_error:
                error_msg = str(model_error)
                print(f"❌ Model {model_name} failed: {error_msg[:150]}...")
                GEMINI_LLM = None
                continue
        
        if successful_model:
            LLM_INITIALIZED = True
            print(f"🚀 Successfully initialized with model: {successful_model}")
            
            # Now configure with optimal settings for comprehensive responses
            GEMINI_LLM = ChatGoogleGenerativeAI(
                model=successful_model, 
                temperature=0.3,  # Natural, helpful responses
                google_api_key=api_key,
                max_retries=2,
                timeout=60,  # Increased timeout
                max_output_tokens=1000,  # Allow more detailed responses
                top_p=0.8,
                top_k=40
            )
            
        else:
            raise Exception("All Gemini models failed")
        
    except Exception as e:
        print(f"❌ Gemini initialization error: {e}")
        print("🔄 Falling back to enhanced keyword system...")
        GEMINI_LLM = None
        LLM_INITIALIZED = False

def load_vector_store(db_path: str = VECTOR_DB_PATH) -> FAISS:
    global VECTOR_DB
    if not os.path.exists(db_path):
        print(f"⚠️ FAISS index not found at {db_path}")
        return None 
        
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    print("✅ FAISS index loaded successfully")
    return vector_store

# --- Initialize Vector Store ---
print("🔄 Initializing vector store...")
VECTOR_DB = load_vector_store()
print("🔄 Vector store initialization complete.")

def llm_generate(prompt: str, system_instruction: str = None) -> str:
    global GEMINI_LLM, LLM_INITIALIZED
    
    if not LLM_INITIALIZED or GEMINI_LLM is None:
        return "ERROR: Gemini LLM is not available. Using fallback mode."

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=prompt)
    ]
        
    try:
        # Add small delay to avoid rate limits
        time.sleep(1)  # Increased delay
        response = GEMINI_LLM.invoke(messages)
        
        # Check if response is empty
        if not response or not response.content:
            return "I apologize, but I couldn't generate a response. Please try again or rephrase your question."
        
        return response.content
        
    except Exception as e:
        print(f"❌ LLM API Call Error: {type(e).__name__}: {e}")
        return f"Service temporarily unavailable. Please try again later."

# --- Enhanced Fallback System ---
def enhanced_fallback_response(query: str, system_instruction: str = None) -> str:
    """Enhanced fallback when Gemini is unavailable"""
    query_lower = query.lower()
    
    if "query understanding" in str(system_instruction).lower():
        topic = "general"
        focus_areas = []
        
        if any(k in query_lower for k in ["aadhar", "aadhaar", "uidai"]): 
            topic = "aadhar"
            if "mobile" in query_lower or "link" in query_lower:
                focus_areas = ["mobile linking", "verification", "biometric", "documents"]
            elif "update" in query_lower or "correction" in query_lower:
                focus_areas = ["data update", "correction process", "documents", "verification"]
            elif "enrollment" in query_lower or "apply" in query_lower:
                focus_areas = ["enrollment process", "documents", "centers", "biometric"]
            elif "form" in query_lower:
                focus_areas = ["form filling", "fields", "documents", "submission"]
            else:
                focus_areas = ["general information", "procedures", "requirements", "centers"]
            
        action = "respond"
        if any(k in query_lower for k in ["form", "fill", "field", "step"]):
            action = "form_assistance"
        elif any(k in query_lower for k in ["where", "location", "center", "office"]):
            action = "location_service"
            
        return json.dumps({
            "intent": "information_request", 
            "topic": topic, 
            "action_required": action,
            "complexity": "detailed",
            "focus_areas": focus_areas
        })
    
    # Pre-defined comprehensive responses for Aadhaar queries
    if any(k in query_lower for k in ["mobile", "link", "number", "aadhar"]):
        return "I'll help you link your mobile number with Aadhaar:\n\n• Visit any Aadhaar enrollment center with your original Aadhaar card and valid ID proof for verification\n• Fill the mobile linking form completely with your current mobile number and accurate personal details\n• Provide biometric verification through fingerprint or iris scan for authentication and security purposes\n• Collect the acknowledgement slip with update request number (URN) for tracking the application status\n• Your mobile number will be linked within 24-48 hours after successful verification process\n• You'll receive SMS confirmation once the mobile linking process is successfully completed"
    
    elif any(k in query_lower for k in ["update", "correction", "change", "aadhar"]):
        return "Here's the complete process for Aadhaar data update/correction:\n\n• Visit the nearest Aadhaar Enrollment Center with original documents that need to be updated\n• Fill the Aadhaar Update/Correction Form carefully with all required changes and information\n• Submit supporting documents as proof for the changes you want to make in your Aadhaar\n• Provide biometric authentication for verification and security purposes during the process\n• Pay the applicable fee (if any) and collect the acknowledgement receipt with URN number\n• The updates will be processed within 5-7 working days and you can check status online"
    
    elif any(k in query_lower for k in ["enrollment", "apply", "new", "aadhar"]):
        return "Complete Aadhaar enrollment process guide:\n\n• Locate the nearest Aadhaar Enrollment Center through UIDAI website or mobile application\n• Carry original documents including proof of identity, proof of address, and date of birth proof\n• Fill the enrollment form completely with accurate personal and demographic information\n• Provide biometric data including fingerprints, iris scan, and photograph at the center\n• Review all entered details carefully before final submission to avoid future corrections\n• Collect the acknowledgement slip containing enrollment ID (EID) for tracking application status"
    
    elif any(k in query_lower for k in ["form", "field", "fill", "aadhar"]):
        return "Detailed Aadhaar form filling guidance:\n\n1. Personal Details Section: Carefully enter full name, gender, date of birth exactly as per documents\n2. Address Information: Provide complete residential address with PIN code and contact details\n3. Document Details: Mention all supporting documents being submitted for verification process\n4. Declaration Section: Read all terms carefully and sign the form only after verifying all entries\n5. Review Process: Double-check all information for accuracy before submitting the form\n6. Supporting Documents: Ensure all original documents match the information provided in the form"
    
    elif any(k in query_lower for k in ["where", "location", "center", "office", "aadhar"]):
        return "I'd be happy to help you find the nearest Aadhaar enrollment centers! To give you the most accurate locations and service availability, could you please share your city name or postal code? This helps me provide you with the most convenient options based on your current location and ensure you visit an authorized UIDAI center."
    
    elif any(k in query_lower for k in ["document", "required", "need", "aadhar"]):
        return "Comprehensive list of documents required for Aadhaar services:\n\n• Proof of Identity: Passport, PAN card, Driving License, Voter ID, or any government issued photo ID\n• Proof of Address: Utility bills, Bank statements, Rental agreement, or any valid address proof document\n• Date of Birth Proof: Birth certificate, SSLC certificate, Passport, or any recognized DOB document\n• For specific services: Additional documents may be required based on the type of Aadhaar service\n• All documents must be original and valid, photocopies are not accepted for verification purposes\n• Carry multiple documents if available to ensure smooth processing at the enrollment center"
    
    else:
        return "I can help with various Aadhaar services including enrollment, mobile linking, data updates, form assistance, document requirements, and location services. Please ask about specific Aadhaar procedures or requirements you need assistance with."

# --- Enhanced Agent Classes ---
class QueryUnderstandingAgent:
    def process(self, query: str) -> Dict[str, Any]:
        if not LLM_INITIALIZED:
            # Use enhanced fallback
            result_json = enhanced_fallback_response(query, "query understanding")
            return json.loads(result_json)
            
        prompt = f"QUERY: {query}\nOUTPUT JSON ONLY:"
        
        json_output = llm_generate(
            prompt=prompt,
            system_instruction=LLM_PROMPT_GUIDELINES["QUERY_UNDERSTANDING"]
        )

        try:
            clean_output = json_output.strip()
            if '```json' in clean_output:
                clean_output = clean_output.split('```json')[1].split('```')[0].strip()
            elif '```' in clean_output:
                clean_output = clean_output.split('```')[1].strip() if len(clean_output.split('```')) > 2 else clean_output.replace('```', '').strip()
            
            parsed = json.loads(clean_output)
            if all(key in parsed for key in ['intent', 'topic', 'action_required']):
                print(f"   🎯 Query Analysis: {parsed.get('topic')} - {parsed.get('action_required')}")
                if parsed.get('focus_areas'):
                    print(f"   🔍 Focus Areas: {parsed.get('focus_areas')}")
                return parsed
            else:
                raise ValueError("Missing required fields")
                
        except (json.JSONDecodeError, AttributeError, KeyError, ValueError) as e:
            print(f"⚠️ LLM JSON parse failed, using fallback: {e}")
            result_json = enhanced_fallback_response(query, "query understanding")
            return json.loads(result_json)

class DocumentRetrievalAgent:
    def process(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        global VECTOR_DB
        
        if VECTOR_DB is None:
            return [{"source": "system_ready", "content": "Knowledge base available"}]
            
        try:
            # Enhanced comprehensive search: Get more documents
            retrieved_docs = VECTOR_DB.similarity_search(query, k=10)  # Increased to 10 for comprehensive coverage
            
            # If we have context about focus areas, do additional searches
            focus_areas = context.get('focus_areas', [])
            additional_docs = []
            
            for focus in focus_areas[:4]:  # Search top 4 focus areas
                try:
                    focus_docs = VECTOR_DB.similarity_search(focus, k=3)
                    additional_docs.extend(focus_docs)
                except:
                    continue
            
            # Also search for related terms
            related_terms = []
            if "aadhar" in query.lower() or context.get('topic') == 'aadhar':
                related_terms = ["uidai", "enrollment", "biometric", "verification", "update"]
            
            for term in related_terms[:3]:
                try:
                    term_docs = VECTOR_DB.similarity_search(term, k=2)
                    additional_docs.extend(term_docs)
                except:
                    continue
            
            # Combine and deduplicate
            all_docs = retrieved_docs + additional_docs
            unique_docs = []
            seen_content = set()
            
            for doc in all_docs:
                content_hash = hash(doc.page_content[:100])  # Simple deduplication
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_docs.append(doc)
            
            # Return up to 12 most relevant documents for comprehensive coverage
            final_docs = unique_docs[:12]
            
            print(f"   📚 Retrieved {len(final_docs)} documents for comprehensive Aadhaar coverage")
            
            return [{"source": doc.metadata.get('source', 'documents'), "content": doc.page_content}
                    for doc in final_docs]
                    
        except Exception as e:
            print(f"❌ Document retrieval error: {e}")
            return [{"source": "system", "content": "Comprehensive document retrieval available"}]

class SummarizationAgent:
    def process(self, docs: List[Dict[str, Any]], query: str) -> str:
        if not LLM_INITIALIZED:
            return enhanced_fallback_response(query, "summarization")
            
        if not docs or docs[0].get('source') == 'system_error':
            return "System configuration incomplete. Please contact administrator."

        # Check if we have actual content
        valid_docs = [doc for doc in docs if doc.get('content') and len(doc['content'].strip()) > 10]
        if not valid_docs:
            return enhanced_fallback_response(query, "summarization")

        context_parts = []
        total_length = 0
        max_context_length = 2500  # Increased for more comprehensive context
        
        for doc in valid_docs:
            if total_length + len(doc['content']) <= max_context_length:
                context_parts.append(doc['content'])
                total_length += len(doc['content'])
            else:
                break
                
        if not context_parts:
            return enhanced_fallback_response(query, "summarization")
                
        context_text = "\n---\n".join(context_parts)
        
        prompt = f"USER QUESTION: {query}\nRETRIEVED DOCUMENT CONTEXT:\n{context_text}"
        
        response = llm_generate(
            prompt=prompt,
            system_instruction=LLM_PROMPT_GUIDELINES['SUMMARIZATION']
        )
        
        # Ensure response is not empty
        if not response or len(response.strip()) < 10:
            return enhanced_fallback_response(query, "summarization")
            
        return response

class ActionPlanningAgent:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = context.get("intent", "information_request")
        topic = context.get("topic", "general")
        action = context.get("action_required", "respond")
        complexity = context.get("complexity", "simple")
        focus_areas = context.get("focus_areas", [])
        
        # More sophisticated decision making with better form detection
        query = context.get("original_query", "").lower()
        
        # Enhanced form detection
        if any(term in query for term in ["form", "fill", "field", "application form", "submit", "apply"]):
            return {
                "action": "form_assistance", 
                "message": "User requires detailed Aadhaar form filling guidance",
                "confidence": "high", 
                "next_steps": ["retrieve_form_docs", "provide_step_by_step_guidance"]
            }
        elif any(term in query for term in ["where", "location", "center", "office", "near me", "address"]):
            return {
                "action": "location_service", 
                "message": "User needs physical Aadhaar service location assistance",
                "confidence": "high",
                "next_steps": ["request_location_details", "provide_finding_instructions"]
            }
        elif topic == "general" and intent == "information_request":
            return {
                "action": "ask", 
                "message": "Need clarification on specific Aadhaar service",
                "confidence": "medium",
                "next_steps": ["suggest_service_options", "request_specifics"]
            }
        else:
            return {
                "action": "respond", 
                "message": f"Comprehensive Aadhaar information response",
                "confidence": "high",
                "next_steps": ["retrieve_comprehensive_docs", "provide_detailed_answers"]
            }

class LocationServiceAgent:
    def process(self, query: str) -> str:
        if not LLM_INITIALIZED:
            return enhanced_fallback_response(query, "location service")
            
        prompt = f"USER QUERY ABOUT AADHAAR LOCATION: {query}"
        response = llm_generate(
            prompt=prompt,
            system_instruction=LLM_PROMPT_GUIDELINES['LOCATION_SERVICE']
        )
        
        # Ensure response is not empty
        if not response or len(response.strip()) < 10:
            return enhanced_fallback_response(query, "location service")
            
        return response

class FormAssistanceAgent:
    def process(self, docs: List[Dict[str, Any]], query: str) -> str:
        if not LLM_INITIALIZED:
            return enhanced_fallback_response(query, "form assistance")
            
        # Check if we have actual content
        valid_docs = [doc for doc in docs if doc.get('content') and len(doc['content'].strip()) > 10]
        if not valid_docs:
            return "No Aadhaar form documentation available for detailed assistance."

        context_parts = []
        total_length = 0
        max_context_length = 1800  # Increased for comprehensive form guidance
        
        for doc in valid_docs:
            if total_length + len(doc['content']) <= max_context_length:
                context_parts.append(doc['content'])
                total_length += len(doc['content'])
            else:
                break
                
        if not context_parts:
            return "No relevant form documentation found for your query."
                
        context_text = "\n---\n".join(context_parts)
        
        prompt = f"AADHAAR FORM-RELATED USER QUERY: {query}\nRETRIEVED FORM DOCUMENTATION:\n{context_text}"
        
        response = llm_generate(
            prompt=prompt,
            system_instruction=LLM_PROMPT_GUIDELINES['FORM_ASSISTANCE']
        )
        
        # Ensure response is not empty
        if not response or len(response.strip()) < 10:
            return enhanced_fallback_response(query, "form assistance")
            
        return response

# --- Initialize LLM ---
print("🔄 Initializing Gemini LLM with temperature 0.3...")
initialize_llm()

if LLM_INITIALIZED:
    print("✅ Gemini LLM initialized successfully with natural response settings!")
else:
    print("⚠️  Using enhanced fallback system")