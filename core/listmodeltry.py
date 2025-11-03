# find_v1beta_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

def find_v1beta_models():
    """Find models that work with v1beta API"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    
    print("🔍 Finding v1beta compatible models...")
    print("=" * 50)
    
    try:
        # List all models to see what's available
        models = genai.list_models()
        
        print(f"📋 Total models available: {len(list(models))}")
        
        # Reset the generator
        models = genai.list_models()
        
        v1beta_models = []
        for model in models:
            model_info = {
                'name': model.name,
                'display_name': getattr(model, 'display_name', 'N/A'),
                'description': getattr(model, 'description', 'N/A'),
            }
            v1beta_models.append(model_info)
        
        print("\n🎯 Available Models in v1beta:")
        for i, model in enumerate(v1beta_models, 1):
            print(f"\n{i}. {model['name']}")
            print(f"   Display: {model['display_name']}")
            print(f"   Desc: {model['description']}")
            
        return v1beta_models
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_v1beta_models():
    """Test specific v1beta model names"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    
    # Common v1beta model patterns
    v1beta_model_patterns = [
        "models/gemini-pro",
        "models/gemini-1.0-pro",
        "models/gemini-1.0-pro-001",
        "models/gemini-pro-vision",
        "models/embedding-001",
        "models/aqa",
        "publishers/google/models/gemini-pro",
        "publishers/google/models/gemini-1.0-pro",
    ]
    
    print("\n🧪 Testing v1beta model patterns:")
    print("=" * 50)
    
    working_models = []
    for model_name in v1beta_model_patterns:
        try:
            print(f"Testing: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say OK")
            print(f"✅ WORKS: {model_name}")
            print(f"   Response: {response.text}")
            working_models.append(model_name)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"❌ NOT FOUND: {model_name}")
            elif "Permission" in error_msg:
                print(f"❌ NO PERMISSION: {model_name}")
            else:
                print(f"❌ ERROR: {model_name} - {error_msg[:100]}")
    
    return working_models

if __name__ == "__main__":
    print("🚀 v1beta Model Finder")
    print("=" * 50)
    
    # Find all available models
    all_models = find_v1beta_models()
    
    # Test specific patterns
    working = test_v1beta_models()
    
    if working:
        print(f"\n🎉 SUCCESS! Use these models:")
        for model in working:
            print(f"   📌 {model}")
    else:
        print("\n❌ No working models found.")
        print("\n💡 SOLUTIONS:")
        print("1. Enable Generative AI API in Google Cloud Console")
        print("2. Check if billing is enabled")
        print("3. Try creating a new API key")
        print("4. Use a different Google Cloud project")