"""
Seed sample FAQs to reach 50+ count for demonstration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from core.models import FAQ, Service
from core.embeddings import get_transformer
from datetime import datetime

# Sample FAQs for various government services
SAMPLE_FAQS = [
    # Passport FAQs
    ("How long does it take to get a passport?", "Normal processing takes 30-45 days from the date of application. Tatkal service is available for urgent cases and takes 3-7 days.", "passport", "general"),
    ("What documents are required for passport application?", "You need proof of identity (Aadhaar, PAN), proof of address (utility bills, rent agreement), and date of birth proof (birth certificate, school certificate).", "passport", "documents"),
    ("Can I track my passport application status?", "Yes, you can track your application status online using your file number on the Passport Seva portal.", "passport", "tracking"),
    ("What is the passport application fee?", "For adults, the fee is Rs. 1,500 for normal processing and Rs. 3,500 for Tatkal. For minors, it's Rs. 1,000 and Rs. 2,000 respectively.", "passport", "fees"),
    ("How do I renew my expired passport?", "You can renew your passport online through the Passport Seva portal. The process is similar to new application but simpler.", "passport", "renewal"),
    
    # Aadhaar FAQs
    ("How can I update my Aadhaar details?", "You can update your Aadhaar details online through the UIDAI portal or by visiting an Aadhaar enrollment center.", "aadhaar", "update"),
    ("Is Aadhaar mandatory for all citizens?", "While not legally mandatory, Aadhaar is required for many government services, subsidies, and benefits.", "aadhaar", "general"),
    ("How do I download my e-Aadhaar?", "Visit the UIDAI website, enter your Aadhaar number and OTP, and download your e-Aadhaar PDF.", "aadhaar", "download"),
    ("What is Aadhaar masking?", "Aadhaar masking hides the first 8 digits of your Aadhaar number for privacy. Only the last 4 digits are visible.", "aadhaar", "privacy"),
    ("Can I link my mobile number to Aadhaar?", "Yes, you can link your mobile number by visiting an Aadhaar center or using the OTP-based online service.", "aadhaar", "linking"),
    
    # PAN Card FAQs
    ("How do I apply for a new PAN card?", "You can apply online through the NSDL or UTIITSL websites by filling Form 49A and submitting required documents.", "pan", "application"),
    ("What is the PAN card application fee?", "The fee is Rs. 107 for Indian addresses and Rs. 1,020 for foreign addresses.", "pan", "fees"),
    ("How long does it take to receive a PAN card?", "It typically takes 15-20 days to receive your PAN card at your registered address.", "pan", "timeline"),
    ("Can I have multiple PAN cards?", "No, having multiple PAN cards is illegal. Each person can have only one PAN.", "pan", "general"),
    ("How do I link PAN with Aadhaar?", "You can link PAN with Aadhaar online through the Income Tax e-filing portal or by SMS.", "pan", "linking"),
    
    # EPFO FAQs
    ("How can I check my EPF balance?", "You can check your EPF balance through the EPFO portal, UMANG app, or by giving a missed call to 9966044425.", "epfo", "balance"),
    ("When can I withdraw my EPF?", "You can withdraw EPF after retirement, resignation (after 2 months of unemployment), or for specific purposes like medical emergency or home purchase.", "epfo", "withdrawal"),
    ("How do I transfer my EPF from previous employer?", "Submit a transfer claim through the EPFO portal using your UAN. The process is online and paperless.", "epfo", "transfer"),
    ("What is UAN in EPF?", "Universal Account Number (UAN) is a unique 12-digit number assigned to each EPF member for life.", "epfo", "general"),
    ("How do I activate my UAN?", "Visit the EPFO portal, enter your UAN, verify with OTP, and set your password to activate.", "epfo", "activation"),
    
    # Driving License FAQs
    ("What documents are required for driving license?", "You need age proof, address proof, passport-size photos, and learner's license for permanent DL application.", "parivahan", "documents"),
    ("How do I renew my driving license?", "You can renew your DL online through the Parivahan portal or by visiting your local RTO.", "parivahan", "renewal"),
    ("What is the validity of a driving license?", "A driving license is valid for 20 years from the date of issue or until the holder turns 50, whichever is earlier.", "parivahan", "validity"),
    ("Can I apply for an international driving permit?", "Yes, you can apply for an IDP at your local RTO if you have a valid Indian driving license.", "parivahan", "international"),
    ("How do I check my driving license status?", "You can check your DL status online on the Parivahan portal using your application number.", "parivahan", "status"),
    
    # Income Tax FAQs
    ("Who needs to file income tax returns?", "Individuals with annual income above Rs. 2.5 lakh (Rs. 3 lakh for senior citizens) must file ITR.", "income_tax", "filing"),
    ("What is the last date for filing ITR?", "The deadline is usually July 31st for individuals and September 30th for businesses, subject to extensions.", "income_tax", "deadline"),
    ("How do I file ITR online?", "Register on the Income Tax e-filing portal, select appropriate ITR form, fill details, and submit with verification.", "income_tax", "online"),
    ("What is Form 16?", "Form 16 is a TDS certificate issued by employers showing salary paid and tax deducted.", "income_tax", "forms"),
    ("Can I revise my ITR?", "Yes, you can revise your ITR before the end of the assessment year or before completion of assessment.", "income_tax", "revision"),
    
    # GST FAQs
    ("What is GST registration threshold?", "Businesses with annual turnover above Rs. 40 lakh (Rs. 20 lakh for special category states) must register for GST.", "gst", "registration"),
    ("How do I file GST returns?", "File GST returns online through the GST portal by the due date based on your registration type.", "gst", "returns"),
    ("What is the GST rate structure?", "GST has multiple slabs: 0%, 5%, 12%, 18%, and 28%, depending on the goods or services.", "gst", "rates"),
    ("Can I claim input tax credit?", "Yes, registered taxpayers can claim ITC on purchases used for business purposes.", "gst", "credit"),
    ("What is GSTIN?", "GSTIN is a unique 15-digit identification number assigned to every GST registered business.", "gst", "general"),
    
    # Voter ID FAQs
    ("How do I apply for a voter ID card?", "You can apply online through the National Voter Service Portal or submit Form 6 at your local electoral office.", "voter_id", "application"),
    ("What is the minimum age for voter ID?", "You must be 18 years or older on the qualifying date to be eligible for voter registration.", "voter_id", "eligibility"),
    ("How do I check if my name is in the voter list?", "Check your name on the NVSP portal or CEO website of your state using your details.", "voter_id", "verification"),
    ("Can I vote from anywhere in India?", "No, you can only vote from the constituency where you are registered.", "voter_id", "voting"),
    ("How do I change my address in voter ID?", "Submit Form 8 online or offline to update your address in the electoral roll.", "voter_id", "update"),
    
    # Ration Card FAQs
    ("How do I apply for a ration card?", "Apply through your state's food and civil supplies department website or visit the local office.", "ration_card", "application"),
    ("What are the types of ration cards?", "There are three types: APL (Above Poverty Line), BPL (Below Poverty Line), and AAY (Antyodaya Anna Yojana).", "ration_card", "types"),
    ("What documents are required for ration card?", "You need address proof, identity proof, income certificate, and passport-size photos.", "ration_card", "documents"),
    ("How do I add a family member to my ration card?", "Submit an application with required documents to your local ration office or online portal.", "ration_card", "addition"),
    ("Can I transfer my ration card to another state?", "Yes, under the One Nation One Ration Card scheme, you can use your card in any state.", "ration_card", "portability"),
]

def seed_faqs():
    """Seed sample FAQs into the database"""
    db = SessionLocal()
    try:
        # Get embedding model
        print("Loading embedding model...")
        model = get_transformer()
        
        # Get existing FAQ count
        existing_count = db.query(FAQ).count()
        print(f"Current FAQ count: {existing_count}")
        
        if existing_count >= 50:
            print("Already have 50+ FAQs. No seeding needed.")
            return
        
        # Get a default service for FAQs without specific service
        default_service = db.query(Service).first()
        
        added_count = 0
        for question, answer, service_name, category in SAMPLE_FAQS:
            # Check if FAQ already exists
            existing = db.query(FAQ).filter(FAQ.question == question).first()
            if existing:
                continue
            
            # Find service by name
            service = db.query(Service).filter(Service.name.ilike(f"%{service_name}%")).first()
            if not service:
                service = default_service
            
            # Generate embeddings
            question_embedding = model.encode(question).tolist()
            answer_embedding = model.encode(answer).tolist()
            
            # Create FAQ
            faq = FAQ(
                question=question,
                answer=answer,
                category=category,
                service_id=service.service_id if service else None,
                question_embedding=question_embedding,
                answer_embedding=answer_embedding,
                language="en"
            )
            
            db.add(faq)
            added_count += 1
            
            if (existing_count + added_count) >= 50:
                break
        
        db.commit()
        
        final_count = db.query(FAQ).count()
        print(f"\n✅ Seeding complete!")
        print(f"   Added: {added_count} FAQs")
        print(f"   Total: {final_count} FAQs")
        print(f"   Status: {'✅ Target reached!' if final_count >= 50 else f'⚠️  Need {50 - final_count} more'}")
        
    except Exception as e:
        print(f"❌ Error seeding FAQs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_faqs()
