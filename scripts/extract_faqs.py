#!/usr/bin/env python
"""Extract FAQs from all scrapers and store in database."""
import sys
sys.path.insert(0, '.')

from data.ingestion.scrapers import get_all_scrapers
from core.database import SessionLocal
from core.models import FAQ, Service
from core.embeddings import get_transformer

def main():
    print('=== EXTRACTING FAQs FROM ALL SCRAPERS ===')
    scrapers = get_all_scrapers()
    print(f'Found {len(scrapers)} scrapers\n')

    db = SessionLocal()
    embedding_model = get_transformer()
    total_new = 0

    try:
        # Get service mappings
        services = {s.name.lower(): s.service_id for s in db.query(Service).all()}
        
        for name, scraper_cls in scrapers.items():
            print(f'--- {name.upper()} ---')
            try:
                scraper = scraper_cls()
                faqs_data = scraper.get_faqs(headless=True)
                print(f'  Extracted: {len(faqs_data)} FAQs')
                
                # Find matching service
                service_id = None
                for service_name, sid in services.items():
                    if name.lower() in service_name or service_name in name.lower():
                        service_id = sid
                        break
                
                if not service_id:
                    service_id = list(services.values())[0] if services else 1
                
                # Insert FAQs
                added = 0
                for faq_data in faqs_data:
                    existing = db.query(FAQ).filter(
                        FAQ.question == faq_data['question']
                    ).first()
                    
                    if existing:
                        continue
                    
                    q_emb = embedding_model.encode(faq_data['question']).tolist()
                    a_emb = embedding_model.encode(faq_data['answer']).tolist()
                    
                    faq = FAQ(
                        service_id=service_id,
                        question=faq_data['question'],
                        answer=faq_data['answer'],
                        short_answer=faq_data['answer'][:200],
                        category=name,
                        language='en',
                        question_embedding=q_emb,
                        answer_embedding=a_emb
                    )
                    db.add(faq)
                    added += 1
                    total_new += 1
                
                db.commit()
                print(f'  ✓ Added: {added} new FAQs')
                
            except Exception as e:
                print(f'  ✗ Error: {str(e)[:100]}')
                db.rollback()
        
        print(f'\n=== SUMMARY ===')
        print(f'New FAQs added: {total_new}')
        print(f'Total FAQs in DB: {db.query(FAQ).count()}')
        
    finally:
        db.close()

if __name__ == '__main__':
    main()

