import re
from urllib.parse import urlparse


class InstagramCollector:

    def __init__(self):
        self.platform = "instagram"

    def extract_username(self, profile_url):

        if not isinstance(profile_url, str) or not profile_url.strip():
            raise ValueError("Instagram profile URL is required.")

        profile_url = profile_url.strip()

        if not profile_url.startswith(("https://", "http://")):
            profile_url = "https://" + profile_url

        parsed_url = urlparse(profile_url)

        allowed_domains = {
            "instagram.com",
            "www.instagram.com"
        }

        if parsed_url.netloc.lower() not in allowed_domains:
            raise ValueError("Invalid Instagram profile URL.")

        path = parsed_url.path.strip("/")

        if not path:
            raise ValueError("Instagram username is missing.")

        username = path.split("/")[0]

        if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", username):
            raise ValueError("Invalid Instagram username.")

        reserved_paths = {
            "accounts", "about", "explore", "direct",
            "reels", "stories", "developer"
        }

        if username.lower() in reserved_paths:
            raise ValueError("This is not a profile URL.")

        return username

    def collect_profile(self, profile_url):

        username = self.extract_username(profile_url)

        return {
            "platform": "instagram",
            "username": username,
            "profile_url": f"https://www.instagram.com/{username}/",
            "collection_status": "pending",
            "message": (
                "Username extracted successfully. "
                "Authorised Instagram API access is required "
                "to retrieve profile information."
            ),
            "profile_data": None
        }


if __name__ == "__main__":

    collector = InstagramCollector()

    test_url = "https://www.instagram.com/sunflower_demo/"

    try:
        result = collector.collect_profile(test_url)

        print("\nINSTAGRAM PROFILE COLLECTOR")
        print("=" * 40)

        for key, value in result.items():
            print(f"{key}: {value}")

    except ValueError as error:
        print("Error:", error)
