import os
from pathlib import Path
from urllib.parse import urlparse

import pymysql
from dotenv import load_dotenv


# Load .env from the main project folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def normalize_profile_url(profile_url: str) -> str:
    """Normalize a profile URL for exact comparison."""
    if not profile_url:
        return ""

    value = profile_url.strip()

    if "://" not in value:
        value = "https://" + value

    parsed = urlparse(value)
    host = (parsed.hostname or "").casefold()

    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.rstrip("/")

    return f"{host}{path}".casefold()


def get_db_connection():
    """Connect to the project's MySQL database."""
    password = os.getenv("MYSQL_PASSWORD")

    if not password:
        raise RuntimeError(
            "MYSQL_PASSWORD is missing. Check the .env file "
            "in the main project folder."
        )

    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password=password,
        database="fake_profile_detection",
        cursorclass=pymysql.cursors.DictCursor
    )


def find_duplicate_profiles(submitted_profile: dict) -> list:
    """Find exact normalized URL matches on the same platform."""
    platform = submitted_profile.get("platform", "").strip().casefold()

    submitted_url = normalize_profile_url(
        submitted_profile.get("profile_url", "")
    )

    if not platform or not submitted_url:
        raise ValueError("Platform and profile URL are required.")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, platform, profile_url, platform_user_id
                FROM profiles
                WHERE LOWER(platform) = %s
                """,
                (platform,)
            )

            existing_profiles = cursor.fetchall()

        matches = []

        for profile in existing_profiles:
            existing_url = normalize_profile_url(
                profile["profile_url"] or ""
            )

            if existing_url and existing_url == submitted_url:
                matches.append({
                    "profile_id": profile["id"],
                    "platform": profile["platform"],
                    "profile_url": profile["profile_url"],
                    "platform_user_id": profile["platform_user_id"],
                    "match_type": "exact_normalized_url_match"
                })

        return matches

    finally:
        connection.close()


if __name__ == "__main__":
    # Fictional test profile.
    test_profile = {
        "platform": "instagram",
        "profile_url": "https://www.instagram.com/sunflower_demo/"
    }

    try:
        results = find_duplicate_profiles(test_profile)

        print("DATABASE DUPLICATE DETECTION")
        print("----------------------------")
        print(f"Matches found: {len(results)}")

        for result in results:
            print(result)

        if not results:
            print("No exact URL matches found.")

    except (pymysql.MySQLError, RuntimeError, ValueError) as error:
        print("Detection failed:", error)

