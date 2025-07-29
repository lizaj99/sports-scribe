"""
Data Validation Module

This module provides utilities for validating and cleaning sports data
to ensure consistency and accuracy across the system.
"""

import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Utility class for validating sports data.
    """

    @staticmethod
    def validate_game_data(game_data: dict[str, Any]) -> bool:
        required_fields = ["fixture_id", "home_team", "away_team", "date"]

        for field in required_fields:
            if field not in game_data:
                logger.warning(f"Missing required field: {field}")
                return False

        if not isinstance(game_data["fixture_id"], int):
            logger.warning("fixture_id must be an integer")
            return False

        if not all(isinstance(game_data.get(key), str) and game_data[key].strip() for key in ["home_team", "away_team"]):
            logger.warning("home_team and away_team must be non-empty strings")
            return False

        try:
            datetime.strptime(game_data["date"], "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format: {game_data['date']}")
            return False

        ft_score = game_data.get("score", {}).get("ft")
        if not (isinstance(ft_score, list) and len(ft_score) == 2 and all(isinstance(x, int) for x in ft_score)):
            logger.warning(f"Invalid FT score: {ft_score}")
            return False

        return True

    @staticmethod
    def validate_fixture(fixture: dict[str, Any]) -> tuple[bool, int, list[str]]:
        issues = []
        required_fields = ["date", "round", "team1", "team2", "score"]

        for field in required_fields:
            if field not in fixture:
                issues.append(f"Missing field: {field}")

        try:
            datetime.strptime(fixture.get("date", ""), "%Y-%m-%d")
        except ValueError:
            issues.append("Invalid date format (expected YYYY-MM-DD)")

        score = fixture.get("score", {}).get("ft", [])
        if not isinstance(score, list) or len(score) != 2 or not all(isinstance(s, int) for s in score):
            issues.append("Invalid or missing full-time score (score.ft)")

        score_value = 100 - len(issues) * 20
        score_value = max(0, score_value)

        return (len(issues) == 0), score_value, issues

    @staticmethod
    def validate_team_data(team_data: dict[str, Any]) -> bool:
        required_fields = ["team_id", "name", "league"]

        for field in required_fields:
            if field not in team_data:
                logger.warning(f"Missing required field: {field}")
                return False

        if not isinstance(team_data["team_id"], int):
            logger.warning("team_id must be an integer")
            return False

        if not isinstance(team_data["name"], str) or not team_data["name"].strip():
            logger.warning("Invalid team name")
            return False

        return True

    @staticmethod
    def validate_player_data(player_data: dict[str, Any]) -> bool:
        required_fields = ["player_id", "name", "position", "team"]

        for field in required_fields:
            if field not in player_data:
                logger.warning(f"Missing required field: {field}")
                return False

        return True

    @staticmethod
    def score_game_data(game_data: dict[str, Any]) -> int:
        score = 100
        if "fixture_id" not in game_data:
            score -= 20
        if not game_data.get("home_team") or not game_data.get("away_team"):
            score -= 20
        if "date" not in game_data:
            score -= 20
        try:
            datetime.strptime(game_data.get("date", ""), "%Y-%m-%d")
        except Exception:
            score -= 10
        ft_score = game_data.get("score", {}).get("ft")
        if not (isinstance(ft_score, list) and len(ft_score) == 2):
            score -= 10

        return max(score, 0)


class DataCleaner:
    """
    Utility class for cleaning and normalizing sports data.
    """

    @staticmethod
    def clean_team_name(team_name: str) -> str:
        if not team_name:
            return ""
        cleaned = re.sub(r"\s+", " ", team_name.strip())
        suffixes = [" FC", " F.C.", " CF", " C.F."]
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)]
                break
        return cleaned

    @staticmethod
    def clean_player_name(player_name: str) -> str:
        if not player_name:
            return ""
        cleaned = re.sub(r"\s+", " ", player_name.strip())
        if cleaned.endswith("."):
            cleaned = cleaned[:-1]
        return cleaned.title()

    @staticmethod
    def normalize_date(date_value: str | datetime) -> str:
        if isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d")
        if isinstance(date_value, str):
            formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y"]
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        logger.warning(f"Could not parse date: {date_value}")
        return date_value

    @staticmethod
    def clean_numeric_stats(stats: dict[str, Any]) -> dict[str, Any]:
        cleaned_stats = {}
        for key, value in stats.items():
            if value is None:
                continue
            try:
                if isinstance(value, str):
                    cleaned_value = re.sub(r"[^\d.-]", "", value)
                    if cleaned_value:
                        cleaned_stats[key] = float(cleaned_value)
                elif isinstance(value, int | float):
                    cleaned_stats[key] = float(value)
            except (ValueError, TypeError):
                logger.warning(f"Could not clean numeric value for {key}: {value}")
        return cleaned_stats
