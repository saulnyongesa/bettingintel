from django.core.management.base import BaseCommand
from predictions.models import League, Match, Source, Tip
from django.utils import timezone
import cloudscraper  # <--- NEW LIBRARY
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random


class Command(BaseCommand):
    help = 'Scrape Kenya Premier League tips from Forebet using Cloudscraper'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing Stealth Scraper...")

        # 1. CONFIGURATION
        URL = "https://www.forebet.com/en/football-tips-and-predictions-for-kenya/premier-league"

        # Create a scraper that mimics a real Chrome browser
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        try:
            # Add a small random delay to look human
            time.sleep(random.uniform(1, 3))

            response = scraper.get(URL)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Blocked: {response.status_code}"))
                # If 403 persists here, we must use Selenium (Plan B)
                return

            soup = BeautifulSoup(response.content, 'html.parser')

            source, _ = Source.objects.get_or_create(
                name="Forebet",
                defaults={'url': URL, 'accuracy_score': 75.0}
            )

            league, _ = League.objects.get_or_create(name="Kenya Premier League", country="Kenya")

            # 2. PARSING
            # Forebet often uses 'rcnt' or 'tr_0' / 'tr_1' classes
            rows = soup.find_all('div', class_='rcnt')

            if not rows:
                # Fallback: Try finding rows via table structure if div structure fails
                rows = soup.select('.schema tr')

            self.stdout.write(f"Found {len(rows)} potential matches.")

            count = 0
            for row in rows:
                try:
                    # Extract text safely
                    text_content = row.get_text(" ", strip=True)

                    # A. EXTRACT TEAMS
                    # Try specific classes first
                    home_node = row.find('span', class_='homeTeam')
                    away_node = row.find('span', class_='awayTeam')

                    if home_node and away_node:
                        home_team = home_node.get_text(strip=True)
                        away_team = away_node.get_text(strip=True)
                    else:
                        # Fallback parsing if classes change
                        # Sometimes data is just in <a> tags
                        links = row.find_all('a', class_='tnm')
                        if len(links) >= 2:
                            home_team = links[0].get_text(strip=True)
                            away_team = links[1].get_text(strip=True)
                        else:
                            continue

                    # B. EXTRACT DATE
                    date_node = row.find('div', class_='date_bah')
                    if date_node:
                        date_str = date_node.get_text(strip=True)
                        # Dummy year handling
                        match_date = timezone.now().replace(hour=15, minute=0)
                    else:
                        match_date = timezone.now().replace(hour=16, minute=0)

                    # C. EXTRACT PREDICTION (Correct Score or 1X2)
                    # Forebet predictions are often in specific columns
                    pred_node = row.find('span', class_='forepr')
                    prediction_code = 'X'
                    score_text = "N/A"

                    if pred_node:
                        score_text = pred_node.get_text(strip=True)
                        # Logic: "2 - 0" -> Home Win (1)
                        if '-' in score_text:
                            parts = score_text.split('-')
                            if parts[0] > parts[1]:
                                prediction_code = '1'
                            elif parts[1] > parts[0]:
                                prediction_code = '2'
                            else:
                                prediction_code = 'X'

                    # D. SAVE
                    match, _ = Match.objects.get_or_create(
                        home_team=home_team,
                        away_team=away_team,
                        league=league,
                        defaults={'start_time': match_date}
                    )

                    Tip.objects.get_or_create(
                        match=match,
                        source=source,
                        defaults={
                            'prediction': prediction_code,
                            'analysis_text': f"Forebet Probability Data: {score_text}"
                        }
                    )
                    count += 1
                    self.stdout.write(f"Scraped: {home_team} vs {away_team}")

                except Exception as e:
                    continue

            self.stdout.write(self.style.SUCCESS(f"Success! Scraped {count} tips."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))