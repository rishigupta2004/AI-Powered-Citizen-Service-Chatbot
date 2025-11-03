import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

# =============================================
# CRITICAL FIX: Add parent directory to Python path
# =============================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"🔧 Path configuration:")
print(f"   Current directory: {current_dir}")
print(f"   Parent directory: {parent_dir}")

# =============================================
# CRITICAL FIX: Load environment variables from project root
# =============================================
from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.join(parent_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"❌ .env file not found at: {env_path}")

# Debug environment
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY NOT FOUND!")

# =============================================
# Import agents using absolute import
# =============================================
try:
    # Use absolute import instead of relative import
    from core.llm_agent_logic import (
        QueryUnderstandingAgent,
        DocumentRetrievalAgent,
        SummarizationAgent,
        ActionPlanningAgent,
        LocationServiceAgent,
        FormAssistanceAgent,
        initialize_llm,
        LLM_INITIALIZED,
        GEMINI_LLM
    )
    print("✅ Successfully imported all agents")
except ImportError as e:
    print(f"❌ Failed to import agents: {e}")
    sys.exit(1)

# =============================================
# FastAPI Application
# =============================================
app = FastAPI(
    title="Multi-Agent Chat Service",
    description="A service for routing complex user queries to specialized LLM agents.",
)

@app.on_event("startup")
async def startup_event():
    """Initialize LLM when the FastAPI app starts"""
    print("🚀 Starting FastAPI application...")
    print("🔑 LLM initialization status:")
    print(f"   - LLM Initialized: {LLM_INITIALIZED}")
    print(f"   - LLM Available: {LLM_INITIALIZED and GEMINI_LLM is not None}")
    
    if LLM_INITIALIZED and GEMINI_LLM is not None:
        print("✅ LLM available - API is ready with comprehensive response capabilities!")
    else:
        print("⚠️  LLM not available - API will use enhanced fallback modes")

class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    response: str
    action: str = "respond"
    context: Dict[str, Any] = {}
    sources: List[str] = []

@app.get("/health")
async def health_check():
    """Health check endpoint to verify LLM status"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    return {
        "status": "healthy",
        "llm_initialized": LLM_INITIALIZED,
        "llm_available": LLM_INITIALIZED and GEMINI_LLM is not None,
        "api_key_available": bool(gemini_key),
        "service": "Multi-Agent Chat Service",
        "capabilities": "Comprehensive document search with natural responses"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Processes the user query through the agent pipeline and routes to the appropriate response agent.
    """
    query = request.message
    print(f"\n💬 Received query: {query}")
    
    try:
        # 1. Query Understanding Agent
        q_agent = QueryUnderstandingAgent()
        understanding_result = q_agent.process(query)
        print(f"   Understanding: topic={understanding_result.get('topic')}, action={understanding_result.get('action_required')}")
        
        # CRITICAL FIX: Store original query in context for better action planning
        understanding_result["original_query"] = query
        
        # 2. Document Retrieval Agent
        d_agent = DocumentRetrievalAgent()
        retrieved_docs = d_agent.process(query, understanding_result)
        print(f"   Retrieved {len(retrieved_docs)} documents for comprehensive coverage")
        
        # Prepare list of unique document sources
        doc_sources = []
        if retrieved_docs and retrieved_docs[0].get('source') != 'system_error':
            doc_sources = [doc['source'] for doc in retrieved_docs if doc.get('source')]
        
        # 3. Action Planning Agent (with enhanced context)
        a_agent = ActionPlanningAgent()
        plan = a_agent.process(understanding_result)
        final_action = plan.get("action", "respond")
        print(f"   Action Plan: {final_action} (Confidence: {plan.get('confidence', 'medium')})")
        
        final_response_text = "I'm sorry, I couldn't process that request. Please try rephrasing."

        # --- 4. EXECUTE THE PLANNED ACTION ---
        if final_action == "form_assistance":
            print("   → Routing to FormAssistanceAgent for comprehensive form guidance")
            f_agent = FormAssistanceAgent()
            final_response_text = f_agent.process(retrieved_docs, query)
            
        elif final_action == "location_service":
            print("   → Routing to LocationServiceAgent for location help")
            l_agent = LocationServiceAgent()
            final_response_text = l_agent.process(query)

        elif final_action == "ask":
            print("   → Asking for clarification")
            final_response_text = plan.get("message", "Please clarify your request.")
            
        else: # final_action == "respond"
            print("   → Routing to SummarizationAgent for comprehensive response")
            s_agent = SummarizationAgent()
            final_response_text = s_agent.process(retrieved_docs, query)

        # --- 5. COMPOSE FINAL RESPONSE ---
        updated_context = {
            "intent": understanding_result.get("intent", "unknown"),
            "topic": understanding_result.get("topic", "general"),
            "last_action": final_action,
            "complexity": understanding_result.get("complexity", "simple"),
            "focus_areas": understanding_result.get("focus_areas", [])
        }

        # Check response quality and provide fallback if needed
        if not final_response_text or len(final_response_text.strip()) < 20:
            print("   ⚠️ Response too short, using enhanced fallback")
            from core.llm_agent_logic import enhanced_fallback_response
            final_response_text = enhanced_fallback_response(query, "summarization")
        
        print(f"   ✅ Comprehensive response generated successfully")
        print(f"   📝 Response length: {len(final_response_text)} characters")
        
        return ChatResponse(
            response=final_response_text,
            action=final_action,
            context=updated_context,
            sources=list(set(doc_sources))
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        # Enhanced error response with fallback
        from core.llm_agent_logic import enhanced_fallback_response
        fallback_response = enhanced_fallback_response(query, "summarization")
        
        return ChatResponse(
            response=fallback_response if fallback_response else "I encountered an error while processing your request. Please try again.",
            action="error",
            context={"error": str(e)},
            sources=[]
        )

@app.get("/debug/agents")
async def debug_agents():
    """Debug endpoint to check agent status and capabilities"""
    return {
        "llm_initialized": LLM_INITIALIZED,
        "gemini_available": GEMINI_LLM is not None,
        "vector_db_loaded": True,  # Assuming VECTOR_DB is loaded in llm_agent_logic
        "agents_available": {
            "QueryUnderstandingAgent": True,
            "DocumentRetrievalAgent": True,
            "SummarizationAgent": True,
            "ActionPlanningAgent": True,
            "LocationServiceAgent": True,
            "FormAssistanceAgent": True
        },
        "supported_actions": ["respond", "form_assistance", "location_service", "ask", "error"]
    }

@app.post("/test/query")
async def test_query(request: ChatRequest):
    """
    Test endpoint for debugging query processing
    """
    query = request.message
    print(f"\n🔧 TEST QUERY: {query}")
    
    try:
        # Test Query Understanding
        q_agent = QueryUnderstandingAgent()
        understanding_result = q_agent.process(query)
        
        # Test Document Retrieval
        d_agent = DocumentRetrievalAgent()
        retrieved_docs = d_agent.process(query, understanding_result)
        
        # Test Action Planning
        a_agent = ActionPlanningAgent()
        understanding_result["original_query"] = query  # Critical fix
        plan = a_agent.process(understanding_result)
        
        return {
            "query": query,
            "understanding": understanding_result,
            "documents_retrieved": len(retrieved_docs),
            "action_plan": plan,
            "llm_initialized": LLM_INITIALIZED
        }
        
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "llm_initialized": LLM_INITIALIZED
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting development server with enhanced comprehensive responses...")
    print("🔧 Critical fixes applied:")
    print("   - Original query stored in context for better action planning")
    print("   - Enhanced error handling with fallback responses")
    print("   - Response quality validation")
    print("   - Debug endpoints for testing")
    
    uvicorn.run(
        "core.chatbot:app",
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )