import threading
from django.core.cache import cache
from django.core.management import call_command
from django.contrib import messages


class AutoScraperMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Check if the user is a Superuser
        # 2. Check if they are visiting the Dashboard (we don't want this running on Home)
        if request.user.is_authenticated and request.user.is_superuser and request.path == '/dashboard/':

            # 3. Check the "Cooldown" Lock
            # We check if 'is_scraping' exists in the cache.
            if not cache.get('is_scraping_active'):

                # Create a background thread so the page loads INSTANTLY
                scraper_thread = threading.Thread(target=self.run_background_jobs)
                scraper_thread.daemon = True  # Ensures thread dies if server stops
                scraper_thread.start()

                # Inform the user (Optional - shows on NEXT refresh)
                messages.info(request, "Auto-Scraper started in background! Refresh in 1 minute to see results.")
            else:
                print("Scraper is already running or on cooldown.")

        response = self.get_response(request)
        return response

    def run_background_jobs(self):
        """
        This runs in the background.
        """
        try:
            # SET THE LOCK (Prevent others from running for 60 minutes)
            # 3600 seconds = 1 hour. Change this to 300 for 5 minutes.
            print("--- MIDDLEWARE: Starting Scrapers ---")
            cache.set('is_scraping_active', True, 3600)

            # Run the Master Commands
            call_command('scrape_all')  # Football Matches
            call_command('scrape_news')  # Pulse Sports News

            print("--- MIDDLEWARE: Scrapers Finished ---")

        except Exception as e:
            print(f"Middleware Scraper Error: {e}")
            # If it fails, release the lock so we can try again
            cache.delete('is_scraping_active')