from django.core.management.base import BaseCommand
from news.models import NewsArticle
import cloudscraper
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Scrape football news from Pulse Sports Kenya'

    def handle(self, *args, **kwargs):
        self.stdout.write("Scraping Pulse Sports...")

        # Pulse Sports Football Section
        URL = "https://www.pulsesports.co.ke/football"

        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )

        try:
            response = scraper.get(URL)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch: {response.status_code}"))
                return

            soup = BeautifulSoup(response.content, 'html.parser')

            # Pulse uses 'article' tags usually, or specific divs
            # We look for the main article links
            articles = soup.find_all('article')  # Generic HTML5 tag often used

            if not articles:
                # Fallback if they use divs
                articles = soup.find_all('div', class_='c-article-card')

            count = 0
            for article in articles:
                try:
                    # 1. Extract Link & Title
                    link_tag = article.find('a')
                    if not link_tag: continue

                    relative_url = link_tag.get('href')
                    if not relative_url: continue

                    # Ensure full URL
                    full_url = relative_url if relative_url.startswith(
                        'http') else f"https://www.pulsesports.co.ke{relative_url}"

                    # Extract Title (try h1, h2, h3)
                    title_tag = article.find(['h1', 'h2', 'h3'])
                    if not title_tag: continue
                    title = title_tag.get_text(" ", strip=True)

                    # 2. Extract Image (Handle Lazy Loading)
                    img_tag = article.find('img')
                    image_url = ""
                    if img_tag:
                        # Pulse uses 'data-src' often for lazy loading
                        image_url = img_tag.get('data-src') or img_tag.get('src') or ""

                    # 3. Save to DB
                    # using update_or_create to avoid duplicates but update generic info
                    obj, created = NewsArticle.objects.get_or_create(
                        url=full_url,
                        defaults={
                            'title': title,
                            'image_url': image_url,
                            'summary': "Click to read full story on Pulse Sports."
                        }
                    )

                    if created:
                        count += 1
                        self.stdout.write(f"Saved: {title[:30]}...")

                except Exception:
                    continue

            self.stdout.write(self.style.SUCCESS(f"Successfully scraped {count} new articles."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))