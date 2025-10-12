#!/usr/bin/env python
"""Extract FAQs from Parivahan scraper."""
import sys
sys.path.insert(0, '.')

from data.ingestion.scrapers.parivahan_scraper import ParivahanScraper
from core.database import SessionLocal
from core.models import FAQ, Service
from core.embeddings import get_transformer

def main():
    print('=== EXTRACTING PARIVAHAN FAQs ===')
    db = SessionLocal()
    embedding_model = get_transformer()
    
    try:
        # Get Parivahan/Driving License service
        service = db.query(Service).filter(
            Service.name.ilike('%parivahan%') | Service.name.ilike('%driving%')
        ).first()
        service_id = service.service_id if service else 5
        
        scraper = ParivahanScraper()
        faqs_data = scraper.get_faqs(headless=True)
        print(f'Extracted: {len(faqs_data)} FAQs')
        
        added = 0
        for faq_data in faqs_data:
            # Check if exists
            existing = db.query(FAQ).filter(
                FAQ.question == faq_data['question'],
                FAQ.service_id == service_id
            ).first()
            if existing:
                continue
            
            # Create embeddings
            q_emb = embedding_model.encode(faq_data['question']).tolist()
            a_emb = embedding_model.encode(faq_data['answer']).tolist()
            
            faq = FAQ(
                service_id=service_id,
                question=faq_data['question'],
                answer=faq_data['answer'],
                short_answer=faq_data['answer'][:200],
                category='parivahan',
                language='en',
                question_embedding=q_emb,
                answer_embedding=a_emb
            )
            db.add(faq)
            added += 1
        
        db.commit()
        print(f'✓ Added: {added} new Parivahan FAQs')
        print(f'Total FAQs in DB: {db.query(FAQ).count()}')
        
    except Exception as e:
        print(f'✗ Error: {str(e)}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    main()

