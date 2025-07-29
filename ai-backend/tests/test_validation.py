from tools.data_validation import DataCleaner, DataValidator


def test_fixture_validation():
    print("\n=== Test Fixture Validation ===")

    # Good fixture data
    fixture_good = {
        "fixture_id": 12345,
        "home_team": "Arsenal FC",
        "away_team": "Chelsea FC",
        "date": "2025-05-25",
        "score": {"ft": [2, 1]}
    }

    # Bad fixture: missing fields, bad date
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

    # Good team
    team_good = {
        "team_id": 1,
        "name": "Manchester United FC",
        "league": "Premier League"
    }

    # Bad team: missing name, no league
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


if __name__ == "__main__":
    test_fixture_validation()
    test_team_validation()
    test_cleaners()
