import asyncio
import os

from dotenv import load_dotenv

from tools.data_validation import DataCleaner, DataValidator
from tools.sports_apis import APIFootballClient

load_dotenv()

def test_fixture_validation():
    print("\n=== Test Fixture Validation ===")

    fixture_good = {
        "fixture_id": 12345,
        "home_team": "Arsenal FC",
        "away_team": "Chelsea FC",
        "date": "2025-05-25",
        "score": {"ft": [2, 1]}
    }

    fixture_missing_fields = {
        "home_team": "Liverpool FC",
        "date": "invalid-date",
        "score": {"ft": ["?", 3]}
    }

    for name, fixture in {
        "Good Fixture": fixture_good,
        "Bad Fixture": fixture_missing_fields
    }.items():
        print(f"\n{name}:")
        valid, score, issues = DataValidator.validate_fixture(fixture)
        print(f"Valid: {valid}")
        print(f"Quality Score: {score}")
        print(f"Issues: {issues}")

def test_team_validation():
    print("\n=== Test Team Validation ===")

    team_good = {
        "team_id": 1,
        "name": "Manchester United FC",
        "league": "Premier League"
    }

    team_bad = {
        "team_id": 2
    }

    for name, team in {
        "Good Team": team_good,
        "Bad Team": team_bad
    }.items():
        print(f"\n{name}:")
        valid = DataValidator.validate_team_data(team)
        print(f"Valid: {valid}")

def test_cleaners():
    print("\n=== Test Data Cleaning ===")

    print("Cleaned team name:", DataCleaner.clean_team_name("Liverpool FC"))
    print("Cleaned player name:", DataCleaner.clean_player_name("john smith jr."))
    print("Normalized date:", DataCleaner.normalize_date("May 25, 2025"))

    stats = {
        "goals": " 2 ",
        "xG": "1.23",
        "yellow_cards": None,
        "invalid": "N/A"
    }
    print("Cleaned stats:", DataCleaner.clean_numeric_stats(stats))

def fetch_sample_fixtures():
    return [
        {
            "fixture": {
                "id": 1234567,
                "date": "2024-08-16T20:00:00+00:00",
                "timestamp": 1723833600
            },
            "league": {
                "id": 39,
                "name": "Premier League",
                "season": 2024
            },
            "teams": {
                "home": {"id": 33, "name": "Manchester United FC"},
                "away": {"id": 36, "name": "Fulham FC"}
            },
            "goals": {"home": 1, "away": 0},
            "score": {"halftime": {"home": 0, "away": 0}, "fulltime": {"home": 1, "away": 0}}
        },
        {
            "fixture": {
                "id": 1234568,
                "date": "2024-08-17T12:30:00+00:00",
                "timestamp": 1723885800
            },
            "league": {
                "id": 39,
                "name": "Premier League",
                "season": 2024
            },
            "teams": {
                "home": {"id": 51, "name": "Ipswich Town FC"},
                "away": {"id": 40, "name": "Liverpool FC"}
            },
            "goals": {"home": 0, "away": 2},
            "score": {"halftime": {"home": 0, "away": 0}, "fulltime": {"home": 0, "away": 2}}
        }
    ]

def run_real_fixture_validation(fixture, index):
    print(f"\nAPI Fixture {index}: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
    valid, score, issues = DataValidator.validate_api_football_fixture(fixture)
    print(f"  Valid: {valid}")
    print(f"  Quality Score: {score}")
    if issues:
        print(f"  Issues: {issues}")
    else:
        print("  ✅ No issues found")

async def test_real_api_football_data():
    print("\n=== Test Real API-Football Data Validation ===")
    api_key = os.getenv("API_FOOTBALL_KEY")
    if not api_key:
        print("⚠️  API_FOOTBALL_KEY not found in environment, skipping real API tests")
        return

    try:
        async with APIFootballClient():
            print("Testing validation with API-Football format data...")
            real_fixtures = fetch_sample_fixtures()
            print(f"Testing validation on {len(real_fixtures)} API-Football format fixtures...")
            for i, fixture in enumerate(real_fixtures):
                run_real_fixture_validation(fixture, i + 1)
    except Exception as e:
        print(f"❌ Error testing with API-Football data: {e}")

def run_problem_case(scenario):
    print(f"\n{scenario['name']}:")
    valid, score, issues = DataValidator.validate_api_football_fixture(scenario['data'])
    print(f"  Valid: {valid}")
    print(f"  Quality Score: {score}")
    print(f"  Issues: {issues}")
    if not valid and score < 100:
        print("  ✅ Correctly identified as problematic")
    else:
        print("  ❌ Failed to identify problematic data")

def test_api_football_problematic_data():
    print("\n=== Test API-Football Problematic Data Scenarios ===")

    problematic_api_fixtures = [
        {"name": "Missing Fixture Section", "data": {"league": {"id": 39, "name": "Premier League"}, "teams": {"home": {"id": 33, "name": "Team A"}, "away": {"id": 36, "name": "Team B"}}, "score": {"fulltime": {"home": 1, "away": 0}}}},
        {"name": "Invalid Date Format", "data": {"fixture": {"id": 123, "date": "16/08/2024"}, "league": {"id": 39, "name": "Premier League"}, "teams": {"home": {"id": 33, "name": "Team A"}, "away": {"id": 36, "name": "Team B"}}, "score": {"fulltime": {"home": 1, "away": 0}}}},
        {"name": "Missing Team Names", "data": {"fixture": {"id": 123, "date": "2024-08-16T20:00:00+00:00"}, "league": {"id": 39, "name": "Premier League"}, "teams": {"home": {"id": 33, "name": ""}, "away": {"id": 36, "name": "Team B"}}, "score": {"fulltime": {"home": 1, "away": 0}}}},
        {"name": "Invalid Score Format", "data": {"fixture": {"id": 123, "date": "2024-08-16T20:00:00+00:00"}, "league": {"id": 39, "name": "Premier League"}, "teams": {"home": {"id": 33, "name": "Team A"}, "away": {"id": 36, "name": "Team B"}}, "score": {"fulltime": "1-0"}}},
        {"name": "Negative Scores", "data": {"fixture": {"id": 123, "date": "2024-08-16T20:00:00+00:00"}, "league": {"id": 39, "name": "Premier League"}, "teams": {"home": {"id": 33, "name": "Team A"}, "away": {"id": 36, "name": "Team B"}}, "score": {"fulltime": {"home": -1, "away": 0}}}}
    ]

    for scenario in problematic_api_fixtures:
        run_problem_case(scenario)

def test_validation_edge_cases():
    print("\n=== Test Validation Edge Cases ===")

    edge_cases = [
        {"name": "Perfect Data", "data": {"round": "Matchday 1", "date": "2024-08-16", "team1": "Arsenal FC", "team2": "Chelsea FC", "score": {"ft": [2, 1]}}, "expected_valid": True, "expected_score": 100},
        {"name": "Minimal Valid Data", "data": {"round": "Matchday 1", "date": "2024-08-16", "team1": "A", "team2": "B", "score": {"ft": [0, 0]}}, "expected_valid": True, "expected_score": 100},
        {"name": "Multiple Issues", "data": {"date": "invalid-date", "score": {"ft": "wrong"}}, "expected_valid": False, "expected_score": 0}
    ]

    for case in edge_cases:
        print(f"\n{case['name']}:")
        valid, score, issues = DataValidator.validate_fixture(case['data'])
        print(f"  Valid: {valid} (expected: {case['expected_valid']})")
        print(f"  Score: {score} (expected: {case['expected_score']})")
        print(f"  Issues: {issues}")
        if valid == case['expected_valid'] and score == case['expected_score']:
            print("  ✅ Passed")
        else:
            print("  ❌ Failed")

async def main():
    test_fixture_validation()
    test_team_validation()
    test_cleaners()
    await test_real_api_football_data()
    test_api_football_problematic_data()
    test_validation_edge_cases()

if __name__ == "__main__":
    asyncio.run(main())
