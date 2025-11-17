from django.core.management.base import BaseCommand
from predictions.models import League, Match, Source, Tip
from django.utils import timezone
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
import random


class Command(BaseCommand):
    help = 'Scrape matches with ACCURATE times using Regex pattern matching.'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- STARTING TIME-SENSITIVE SCRAPER ---")

        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        self.now = timezone.now()

        # Run scrapers sequentially
        try:
            self.scrape_forebet()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Forebet Failed: {e}"))

        try:
            self.scrape_betwizad()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"BetWizad Failed: {e}"))

        try:
            self.scrape_footballpredictions()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"FootballPredictions Failed: {e}"))

        self.stdout.write(self.style.SUCCESS("--- SCRAPING COMPLETE ---"))

    # =====================================================
    # HELPER: SMART TIME EXTRACTION
    # =====================================================
    def extract_datetime(self, text_content):
        """
        Scans text for time patterns like '14:30' or '18/11 14:00'.
        Returns a timezone-aware datetime object.
        """
        # 1. Try to find full date+time: "18/11 14:30"
        full_match = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})', text_content)

        if full_match:
            day, month, time_str = full_match.groups()
            # Logic to handle Year (if scraping Dec matches in Jan)
            year = self.now.year
            if self.now.month == 12 and int(month) == 1:
                year += 1

            dt_str = f"{year}-{month}-{day} {time_str}"
            dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return timezone.make_aware(dt_obj)

        # 2. If no date, find just time: "14:30" and assume TODAY (or Tomorrow if time passed)
        time_match = re.search(r'(\d{1,2}:\d{2})', text_content)
        if time_match:
            time_str = time_match.group(1)
            # Combine Today's Date + Found Time
            today_str = self.now.strftime("%Y-%m-%d")
            dt_obj = datetime.strptime(f"{today_str} {time_str}", "%Y-%m-%d %H:%M")
            dt_aware = timezone.make_aware(dt_obj)

            # If that time has already passed significantly (e.g. > 2 hours ago),
            # assume it's a game for TOMORROW (since we filter out past games)
            if dt_aware < (self.now - timedelta(hours=2)):
                dt_aware += timedelta(days=1)

            return dt_aware

        # 3. Last Resort Fallback (Only if NO time found)
        return self.now + timedelta(hours=24)

    def normalize_team_name(self, name):
        name = name.lower().strip()
        fluff = [' fc', 'fc ', 'cf ', ' cf', ' as', 'as ', 'united', 'city', 'town']
        for word in fluff:
            name = name.replace(word, "")
        return name.strip()

    def get_or_create_match(self, home_raw, away_raw, match_date):
        # SKIP PAST GAMES
        if match_date < self.now:
            return None

        clean_home = self.normalize_team_name(home_raw)
        clean_away = self.normalize_team_name(away_raw)

        # Fuzzy match existing games within +/- 4 hours window
        start_window = match_date - timedelta(hours=4)
        end_window = match_date + timedelta(hours=4)

        candidates = Match.objects.filter(
            start_time__range=(start_window, end_window),
            status='scheduled'
        )

        for m in candidates:
            db_home = self.normalize_team_name(m.home_team)
            db_away = self.normalize_team_name(m.away_team)
            if (clean_home in db_home or db_home in clean_home) and \
                    (clean_away in db_away or db_away in clean_away):
                return m

        league, _ = League.objects.get_or_create(name="International", defaults={'country': 'World'})
        return Match.objects.create(
            home_team=home_raw, away_team=away_raw, league=league,
            start_time=match_date, status='scheduled'
        )

    # =====================================================
    # SOURCE 1: FOREBET
    # =====================================================
    def scrape_forebet(self):
        url = "https://www.forebet.com/en/football-tips-and-predictions-for-today"
        self.stdout.write(f"Scraping Forebet...")
        time.sleep(2)

        soup = BeautifulSoup(self.scraper.get(url).content, 'html.parser')
        source, _ = Source.objects.get_or_create(name="Forebet", defaults={'url': url, 'accuracy_score': 80.0})

        rows = soup.find_all('div', class_='rcnt')
        for row in rows:
            try:
                text = row.get_text(" ", strip=True)

                # Extract Teams
                h_node = row.find('span', class_='homeTeam')
                a_node = row.find('span', class_='awayTeam')
                if not h_node or not a_node: continue

                home, away = h_node.text.strip(), a_node.text.strip()

                # Extract Date using NEW Helper
                match_date = self.extract_datetime(text)

                # Extract Score Tip
                score_match = re.search(r'(\d+)\s*-\s*(\d+)', text)
                outcome = 'X'
                analysis = "Draw predicted"
                if score_match:
                    h, a = int(score_match.group(1)), int(score_match.group(2))
                    if h > a:
                        outcome = '1'
                    elif a > h:
                        outcome = '2'
                    analysis = f"Correct Score: {h} - {a}"

                match = self.get_or_create_match(home, away, match_date)
                if match:
                    Tip.objects.get_or_create(match=match, source=source,
                                              defaults={'prediction': outcome, 'analysis_text': analysis})
            except:
                continue

    # =====================================================
    # SOURCE 2: BETWIZAD
    # =====================================================
    def scrape_betwizad(self):
        url = "https://betwizad.com/premier-league/england"
        self.stdout.write(f"Scraping BetWizad...")

        soup = BeautifulSoup(self.scraper.get(url).content, 'html.parser')
        source, _ = Source.objects.get_or_create(name="BetWizad", defaults={'url': url, 'accuracy_score': 65.0})

        # Find generic rows in tables
        rows = soup.find_all('tr')
        for row in rows:
            try:
                text = row.get_text(" ", strip=True)
                # Must look like a match row: contains time (:) and prediction (1/X/2)
                if ":" not in text or len(text) < 20: continue

                cols = row.find_all('td')
                if len(cols) < 4: continue

                # Betwizad usually: Date | Home | Score | Away | Tip
                home = cols[1].get_text(strip=True)
                away = cols[3].get_text(strip=True)
                tip = cols[-1].get_text(strip=True)

                outcome = 'X'
                if '1' in tip:
                    outcome = '1'
                elif '2' in tip:
                    outcome = '2'

                # Extract Date using NEW Helper (looks for HH:MM in the row)
                match_date = self.extract_datetime(text)

                match = self.get_or_create_match(home, away, match_date)
                if match:
                    Tip.objects.get_or_create(match=match, source=source,
                                              defaults={'prediction': outcome, 'analysis_text': f"Tip: {tip}"})
            except:
                continue

    # =====================================================
    # SOURCE 3: FOOTBALLPREDICTIONS.COM
    # =====================================================
    def scrape_footballpredictions(self):
        url = "https://footballpredictions.com/betting-tips/"
        self.stdout.write(f"Scraping FootballPredictions...")

        soup = BeautifulSoup(self.scraper.get(url).content, 'html.parser')
        source, _ = Source.objects.get_or_create(name="FootballPredictions.com",
                                                 defaults={'url': url, 'accuracy_score': 70.0})

        cards = soup.find_all('div', class_='prediction-card')
        if not cards: cards = soup.find_all('article')

        for card in cards:
            try:
                text = card.get_text(" ", strip=True)

                teams_match = re.search(r'([A-Za-z0-9 ]{3,}) vs ([A-Za-z0-9 ]{3,})', text)
                if not teams_match: continue

                home, away = teams_match.group(1).strip(), teams_match.group(2).strip()

                outcome = 'X'
                if "Home Win" in text or "1" in text:
                    outcome = '1'
                elif "Away Win" in text or "2" in text:
                    outcome = '2'

                # Try to find time in text, otherwise stagger it
                # FP usually doesn't list exact time, so we rely on a "safe" future time
                match_date = self.extract_datetime(text)

                # If extract_datetime returns the fallback (meaning no time found),
                # let's push it to tomorrow noon to be safe
                if match_date.hour == self.now.hour:
                    match_date = self.now.replace(hour=13, minute=0) + timedelta(days=1)

                match = self.get_or_create_match(home, away, match_date)
                if match:
                    Tip.objects.get_or_create(match=match, source=source,
                                              defaults={'prediction': outcome, 'analysis_text': "Expert Analysis"})
            except:
                continue