BETTINGINTEL.ONLINE - Data-Driven Football Intelligence
=========================================

BettingIntel.Online is a Django-based data aggregation engine 
designed to eliminate "gut-feeling" betting. It scrapes 
top-tier prediction platforms and uses a consensus engine 
to identify high-confidence value in football markets.

--- 1. CORE FEATURES ---

* Automated Scraping: 24/7 scanning of top prediction sites.
* Consensus Engine: Cross-references multiple sources to 
  generate confidence scores.
* Accuracy Tracking: Historical performance monitoring of 
  every data source.
* Responsive UI: Built with Django and Bootstrap 5.

--- 2. PREREQUISITES ---

* Python 3.8+
* Pip (Python Package Manager)
* Virtualenv
* PostgreSQL (Optional, SQLite3 used by default)

--- 3. INSTALLATION & SETUP ---

1. Clone the repository:
   git clone https://github.com/saulnyongesa/bettingintel.git
   cd bettingintel

2. Create and activate a virtual environment:
   python -m venv venv
   # Windows: 
   venv\Scripts\activate
   # Mac/Linux: 
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure Environment Variables:
   Create a .env file in the root directory:
   DEBUG=True
   SECRET_KEY=your_secret_key_here

5. Run Migrations:
   python manage.py makemigrations
   python manage.py migrate

6. Create Superuser:
   python manage.py createsuperuser

7. Start Development Server:
   python manage.py runserver

--- 4. DIRECTORY STRUCTURE ---

/bettingintel   - Project configuration
/core           - Main logic, views, and prediction models
/scraper        - Background tasks and scraping scripts
/templates      - HTML files (base.html, about.html, etc.)
/static         - CSS, JavaScript, and Images

--- 5. DISCLAIMER ---

BettingIntel.Online is an informational tool. We are not 
a bookmaker and do not accept wagers. Always gamble 
responsibly.

--- 6. CONTACT ---
www.saulmupalia.online
