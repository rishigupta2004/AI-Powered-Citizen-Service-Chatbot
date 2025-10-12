# Project Refinement Plan

## Issues Identified
1. **Frontend:** Fixed - Vite serving correctly now with Tailwind directives and clean imports
2. **FAQs:** Only 6 FAQs (18 placeholders removed) - Need to extract FAQs from scrapers
3. **Broken/Unused Code:** Multiple areas need cleanup and optimization
4. **Cache Files:** Unwanted cache files present

## Refinement Tasks

### 1. Frontend Fixes ✅
- [x] Add missing `@tailwind` directives to globals.css
- [x] Fix versioned imports (@radix-ui, lucide-react)
- [x] Install missing dependencies
- [x] Restart dev server successfully

### 2. Extract FAQs from Live Sources
- [ ] Run FAQ extraction from all scrapers:
  - Passport (multiple FAQ pages)
  - Aadhaar
  - PAN
  - EPFO
  - Parivahan
  - Railways
  - RBI
- [ ] Store extracted FAQs in database
- [ ] Generate embeddings for FAQ search

### 3. Code Cleanup & Optimization
- [ ] Remove unused cache files
- [ ] Consolidate duplicate logic
- [ ] Optimize long files (300+ lines → <100 where possible)
- [ ] Remove dead code and commented sections
- [ ] Update imports to use consistent paths

### 4. Testing & Verification
- [ ] Run all tests to ensure nothing broken
- [ ] Verify warehouse data integrity
- [ ] Check API endpoints functionality
- [ ] Validate frontend-backend integration

### 5. Documentation Update
- [ ] Update README with current setup
- [ ] Document API endpoints
- [ ] Add troubleshooting guide

## Priority Order
1. Extract FAQs (user's main concern)
2. Clean cache files
3. Code optimization
4. Testing
5. Documentation

