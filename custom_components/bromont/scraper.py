"""Bromont Mountain web scraper."""

import aiohttp
import async_timeout
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Optional


class BromontScraper:
    """Scraper for Bromont Mountain conditions page."""

    def __init__(self):
        self.url = "https://www.bromontmontagne.com/conditions-detaillees/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.data = {}

    async def scrape(self) -> Dict:
        """Main scraping method."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url, headers=self.headers) as response:
                        response.raise_for_status()
                        content = await response.read()
                        soup = BeautifulSoup(content, "lxml")

                        # Extract all data sections
                        self.data = {
                            "scraped_at": datetime.now().isoformat(),
                            "date": self._get_date(soup),
                            "hours": self._get_hours(soup),
                            "last_update": self._get_last_update(soup),
                            "accumulations": self._get_accumulations(soup),
                            "conditions": self._get_conditions(soup),
                            "terrain": self._get_terrain(soup),
                            "lifts": self._get_lifts(soup),
                            "trails": self._get_trails(soup),
                            "glades": self._get_glades(soup),
                            "snow_parks": self._get_snow_parks(soup),
                            "alpine_hiking": self._get_alpine_hiking(soup),
                            "snowshoeing": self._get_snowshoeing(soup),
                            "mountain_activities": self._get_mountain_activities(soup),
                            "parking": self._get_parking(soup),
                        }

                        return self.data

        except aiohttp.ClientError as e:
            print(f"Error fetching page: {e}")
            return {}
        except Exception as e:
            print(f"Error parsing data: {e}")
            return {}

    def _get_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract current date."""
        date_elem = soup.find("h1", class_="date_encours")
        return date_elem.text.strip() if date_elem else None

    def _get_hours(self, soup: BeautifulSoup) -> Dict:
        """Extract opening hours."""
        hours_div = soup.find("div", class_="dash-horaire")
        if hours_div:
            hours_span = hours_div.find("span", class_="heures")
            return {"status": hours_span.text.strip() if hours_span else None}
        return {}

    def _get_last_update(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract last update time."""
        update_div = soup.find("div", class_="maj-time")
        if update_div:
            text = update_div.text.strip()
            return text.replace("Mise à jour le", "").strip()
        return None

    def _get_accumulations(self, soup: BeautifulSoup) -> Dict:
        """Extract snow accumulation data."""
        acc_bloc = soup.find("div", id="dash-acc")
        if not acc_bloc:
            return {}

        result = {}

        # Main accumulation (24h)
        main_metric = acc_bloc.find("div", class_="data_metric")
        main_imperial = acc_bloc.find("div", class_="data_imp")

        if main_metric:
            result["24h"] = {
                "metric": main_metric.text.strip(),
                "imperial": main_imperial.text.strip() if main_imperial else None,
            }

        # Sub-info (48h, 7 days, total)
        sub_items = acc_bloc.find_all("li")
        for item in sub_items:
            label = item.find("span", class_="txt-data-label")
            metric = item.find("div", class_="data_metric")
            imperial = item.find("div", class_="data_imp")

            if label and metric:
                period = label.text.strip()
                result[period] = {
                    "metric": metric.text.strip(),
                    "imperial": imperial.text.strip() if imperial else None,
                }

        return result

    def _get_conditions(self, soup: BeautifulSoup) -> Dict:
        """Extract snow conditions."""
        cond_bloc = soup.find("div", id="dash-conditions")
        if not cond_bloc:
            return {}

        result = {}
        labels = cond_bloc.find_all("span", class_="txt-data-label")
        paragraphs = cond_bloc.find_all("p")

        for label, p in zip(labels, paragraphs):
            key = label.text.strip().lower()
            result[key] = p.text.strip()

        return result

    def _get_terrain(self, soup: BeautifulSoup) -> Dict:
        """Extract terrain percentages."""
        terrain_bloc = soup.find("div", id="dash-terrains")
        if not terrain_bloc:
            return {}

        result = {}

        # Top progress (circular)
        top_progress = terrain_bloc.find("div", class_="top-progress")
        if top_progress:
            for block in top_progress.find_all("div", class_="progress-block"):
                title = block.find("span", class_="title-data-big")
                percentage = block.find("span", class_="txt-data-big")
                if title and percentage:
                    result[title.text.strip()] = percentage.text.strip()

        # Bottom progress (linear)
        bottom_progress = terrain_bloc.find("div", class_="bottom-progress")
        if bottom_progress:
            for block in bottom_progress.find_all("div", class_="progress-block"):
                title = block.find("span", class_="title-data-big")
                percentage = block.find("span", class_="txt-data-big")
                if title and percentage:
                    result[title.text.strip()] = percentage.text.strip()

        return result

    def _get_lifts(self, soup: BeautifulSoup) -> Dict:
        """Extract lift status."""
        lifts_bloc = soup.find("div", id="recap-remontes")
        if not lifts_bloc:
            return {}

        result = {"summary": self._get_summary_counts(lifts_bloc), "by_area": {}}

        # Get details by area
        detail_div = lifts_bloc.find("div", class_="dash-detail")
        if detail_div:
            for versant in detail_div.find_all("div", class_="bloc_versant"):
                area_name = versant.find("span", class_="titre")
                if area_name:
                    area = area_name.text.strip()
                    result["by_area"][area] = []

                    for liste in versant.find_all("div", class_="liste"):
                        lift_name = liste.find("span", class_="nom")
                        day_status = liste.find("span", class_="jour")
                        night_status = liste.find("span", class_="soir")
                        realtime_status = liste.find("div", class_="statut")

                        if lift_name:
                            lift_data = {
                                "name": lift_name.text.strip(),
                                "day": day_status.text.strip() if day_status else None,
                                "night": (
                                    night_status.text.strip() if night_status else None
                                ),
                                "realtime": (
                                    realtime_status.text.strip()
                                    if realtime_status
                                    else None
                                ),
                            }
                            result["by_area"][area].append(lift_data)

        return result

    def _get_trails(self, soup: BeautifulSoup) -> Dict:
        """Extract trail status."""
        trails_bloc = soup.find("div", id="recap-pistes")
        if not trails_bloc:
            return {}

        result = {"summary": self._get_summary_counts(trails_bloc), "by_area": {}}

        # Get details by area
        detail_div = trails_bloc.find("div", class_="dash-detail")
        if detail_div:
            for versant in detail_div.find_all("div", class_="bloc_versant"):
                area_name = versant.find("span", class_="titre")
                if area_name:
                    area = area_name.text.strip()
                    result["by_area"][area] = []

                    for liste in versant.find_all("div", class_="liste"):
                        trail_number = liste.find("span", class_="numero")
                        trail_name = liste.find("span", class_="nom")
                        difficulty = liste.find("span", class_="legende")
                        day_status = liste.find("span", class_="jour")
                        night_status = liste.find("span", class_="soir")

                        if trail_name:
                            trail_data = {
                                "number": (
                                    trail_number.text.strip() if trail_number else None
                                ),
                                "name": trail_name.text.strip(),
                                "difficulty": self._extract_difficulty(difficulty),
                                "day": day_status.text.strip() if day_status else None,
                                "night": (
                                    night_status.text.strip() if night_status else None
                                ),
                            }
                            result["by_area"][area].append(trail_data)

        return result

    def _get_glades(self, soup: BeautifulSoup) -> Dict:
        """Extract glade (sous-bois) status."""
        glades_bloc = soup.find("div", id="recap-pistes-ssbois")
        if not glades_bloc:
            return {}

        result = {"summary": self._get_summary_counts(glades_bloc), "by_area": {}}

        # Similar structure to trails
        detail_div = glades_bloc.find("div", class_="dash-detail")
        if detail_div:
            for versant in detail_div.find_all("div", class_="bloc_versant"):
                area_name = versant.find("span", class_="titre")
                if area_name:
                    area = area_name.text.strip()
                    result["by_area"][area] = []

                    for liste in versant.find_all("div", class_="liste"):
                        trail_number = liste.find("span", class_="numero")
                        trail_name = liste.find("span", class_="nom")
                        difficulty = liste.find("span", class_="legende")
                        day_status = liste.find("span", class_="jour")
                        night_status = liste.find("span", class_="soir")

                        if trail_name:
                            trail_data = {
                                "number": (
                                    trail_number.text.strip() if trail_number else None
                                ),
                                "name": trail_name.text.strip(),
                                "difficulty": self._extract_difficulty(difficulty),
                                "day": day_status.text.strip() if day_status else None,
                                "night": (
                                    night_status.text.strip() if night_status else None
                                ),
                            }
                            result["by_area"][area].append(trail_data)

        return result

    def _get_snow_parks(self, soup: BeautifulSoup) -> Dict:
        """Extract snow park status."""
        parks_bloc = soup.find("div", id="recap-snowparks")
        if not parks_bloc:
            return {}

        result = {"summary": self._get_summary_counts(parks_bloc), "parks": []}

        detail_div = parks_bloc.find("div", class_="dash-detail")
        if detail_div:
            for liste in detail_div.find_all("div", class_="liste"):
                park_number = liste.find("span", class_="numero")
                park_name = liste.find("span", class_="nom")
                difficulty = liste.find("span", class_="legende")
                day_status = liste.find("span", class_="jour")
                night_status = liste.find("span", class_="soir")
                location = liste.find("span", class_="emplacement")

                if park_name:
                    park_data = {
                        "number": park_number.text.strip() if park_number else None,
                        "name": park_name.text.strip(),
                        "difficulty": self._extract_difficulty(difficulty),
                        "day": day_status.text.strip() if day_status else None,
                        "night": night_status.text.strip() if night_status else None,
                        "location": (
                            location.text.strip().replace("Emplacement:", "").strip()
                            if location
                            else None
                        ),
                    }
                    result["parks"].append(park_data)

        return result

    def _get_alpine_hiking(self, soup: BeautifulSoup) -> Dict:
        """Extract alpine hiking trail status."""
        alpine_bloc = soup.find("div", id="recap-alpine")
        if not alpine_bloc:
            return {}

        result = {"summary": self._get_summary_counts(alpine_bloc), "trails": []}

        detail_div = alpine_bloc.find("div", class_="dash-detail")
        if detail_div:
            for liste in detail_div.find_all("div", class_="liste"):
                trail_name = liste.find("span", class_="nom")
                difficulty = liste.find("span", class_="legende")
                day_status = liste.find("span", class_="jour")
                night_status = liste.find("span", class_="soir")

                if trail_name:
                    trail_data = {
                        "name": trail_name.text.strip(),
                        "difficulty": self._extract_difficulty(difficulty),
                        "day": day_status.text.strip() if day_status else None,
                        "night": night_status.text.strip() if night_status else None,
                    }
                    result["trails"].append(trail_data)

        return result

    def _get_snowshoeing(self, soup: BeautifulSoup) -> Dict:
        """Extract snowshoeing trail status."""
        raquette_bloc = soup.find("div", id="recap-raquette")
        if not raquette_bloc:
            return {}

        result = {"summary": self._get_summary_counts(raquette_bloc), "trails": []}

        detail_div = raquette_bloc.find("div", class_="dash-detail")
        if detail_div:
            for liste in detail_div.find_all("div", class_="liste"):
                trail_name = liste.find("span", class_="nom")
                difficulty = liste.find("span", class_="legende")
                day_status = liste.find("span", class_="jour")
                night_status = liste.find("span", class_="soir")

                if trail_name:
                    trail_data = {
                        "name": trail_name.text.strip(),
                        "difficulty": self._extract_difficulty(difficulty),
                        "day": day_status.text.strip() if day_status else None,
                        "night": night_status.text.strip() if night_status else None,
                    }
                    result["trails"].append(trail_data)

        return result

    def _get_mountain_activities(self, soup: BeautifulSoup) -> Dict:
        """Extract mountain activities status."""
        activities_bloc = soup.find("div", id="recap-activite")
        if not activities_bloc:
            return {}

        result = {
            "summary": self._get_summary_counts(activities_bloc),
            "activities": [],
        }

        return result

    def _get_parking(self, soup: BeautifulSoup) -> Dict:
        """Extract parking status."""
        parking_bloc = soup.find("div", id="recap-stationnement")
        if not parking_bloc:
            return {}

        result = {"summary": self._get_summary_counts(parking_bloc), "by_area": {}}

        detail_div = parking_bloc.find("div", class_="dash-detail")
        if detail_div:
            for versant in detail_div.find_all("div", class_="bloc_versant"):
                area_name = versant.find("span", class_="titre")
                if area_name:
                    area = area_name.text.strip()
                    result["by_area"][area] = []

                    for liste in versant.find_all("div", class_="liste"):
                        parking_name = liste.find("span", class_="nom")
                        day_status = liste.find("span", class_="jour")
                        night_status = liste.find("span", class_="soir")

                        if parking_name:
                            parking_data = {
                                "name": parking_name.text.strip(),
                                "day": day_status.text.strip() if day_status else None,
                                "night": (
                                    night_status.text.strip() if night_status else None
                                ),
                            }
                            result["by_area"][area].append(parking_data)

        return result

    def _get_summary_counts(self, bloc: BeautifulSoup) -> Dict:
        """Extract summary counts from a bloc."""
        summary = {}
        resume = bloc.find("div", class_="dash-resume")
        if resume:
            day_etat = resume.find("div", class_="etat")
            if day_etat:
                txt_data = day_etat.find("span", class_="txt-data")
                total = day_etat.find("span", class_="total")
                if txt_data and total:
                    summary["day"] = {
                        "open": txt_data.text.strip(),
                        "total": total.text.strip().replace("/", ""),
                    }

            # Find night status (second etat div)
            etats = resume.find_all("div", class_="etat")
            if len(etats) > 1:
                night_etat = etats[1]
                txt_data = night_etat.find("span", class_="txt-data")
                total = night_etat.find("span", class_="total")
                if txt_data and total:
                    summary["night"] = {
                        "open": txt_data.text.strip(),
                        "total": total.text.strip().replace("/", ""),
                    }

        return summary

    def _extract_difficulty(self, difficulty_elem) -> Optional[str]:
        """Extract difficulty level from icon classes."""
        if not difficulty_elem:
            return None

        icon = difficulty_elem.find("i")
        if icon:
            classes = icon.get("class", [])
            for cls in classes:
                if "ico-" in cls:
                    return cls.replace("ico-", "")

        return None
