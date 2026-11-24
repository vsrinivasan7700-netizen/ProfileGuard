from urllib.parse import urlparse


def normalize_username(username: str) -> str:
    """Normalize usernames for case-insensitive comparison."""
    if not username:
        return ""

    return username.strip().lstrip("@").casefold()


def normalize_profile_url(profile_url: str) -> str:
    """Normalize profile URLs for comparison."""
    if not profile_url or not profile_url.strip():
        return ""

    value = profile_url.strip()

    if "://" not in value:
        value = "https://" + value

    parsed = urlparse(value)

    host = (parsed.hostname or "").casefold()

    # Ignore www. when comparing domains.
    if host.startswith("www."):
        host = host[4:]

    # Remove trailing slashes, query parameters, and fragments.
    path = parsed.path.rstrip("/")

    return f"{host}{path}".casefold()


def compare_profiles(profile_a: dict, profile_b: dict) -> dict:
    """
    Compare two profiles for exact username or URL matches.

    An exact match is a signal for further investigation.
    It does not prove impersonation or establish that two
    accounts belong to the same person.
    """

    platform_a = profile_a.get("platform", "").strip().casefold()
    platform_b = profile_b.get("platform", "").strip().casefold()

    username_a = normalize_username(profile_a.get("username", ""))
    username_b = normalize_username(profile_b.get("username", ""))

    url_a = normalize_profile_url(profile_a.get("profile_url", ""))
    url_b = normalize_profile_url(profile_b.get("profile_url", ""))

    reasons = []

    # Compare platform-specific profiles.
    if platform_a and platform_b and platform_a != platform_b:
        return {
            "duplicate_match": False,
            "match_type": "different_platforms",
            "reasons": [
                "Profiles belong to different platforms. "
                "Cross-platform identity needs separate verification."
            ],
        }

    # Compare normalized profile URLs.
    if url_a and url_b and url_a == url_b:
        reasons.append("Exact normalized profile URL match")

    # Compare normalized usernames.
    if username_a and username_b and username_a == username_b:
        reasons.append("Exact normalized username match")

    duplicate_match = bool(reasons)

    return {
        "duplicate_match": duplicate_match,
        "match_type": "exact_match" if duplicate_match else "no_exact_match",
        "reasons": reasons,
    }


if __name__ == "__main__":
    first_profile = {
        "platform": "instagram",
        "username": "@example_user",
        "profile_url": "https://www.instagram.com/example_user/",
    }

    second_profile = {
        "platform": "instagram",
        "username": "EXAMPLE_USER",
        "profile_url": "instagram.com/example_user",
    }

    result = compare_profiles(first_profile, second_profile)

    print("Duplicate Profile Detection Result")
    print("----------------------------------")
    print(f"Duplicate match: {result['duplicate_match']}")
    print(f"Match type: {result['match_type']}")
    print("Reasons:")

    for reason in result["reasons"]:
        print(f"- {reason}")

