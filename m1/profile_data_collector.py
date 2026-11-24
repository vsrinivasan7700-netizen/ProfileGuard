from m1.instagram_collector import InstagramCollector


class ProfileDataCollector:

    def __init__(self):
        self.instagram = InstagramCollector()

    def collect_profile_data(self, profile_url, profile_data):

        profile = self.instagram.collect_profile(profile_url)
        username = profile["username"]

        if not isinstance(profile_data, dict):
            raise ValueError("Profile data must be a dictionary.")

        full_name = profile_data.get("full_name")
        biography = profile_data.get("biography")

        has_profile_picture = profile_data.get(
            "has_profile_picture"
        )

        is_private = profile_data.get("is_private")
        posts = profile_data.get("posts")
        followers = profile_data.get("followers")
        following = profile_data.get("following")

        # External URL:
        # Present with None means confirmed no external URL.
        # Missing key means information unavailable.
        if "external_url" in profile_data:
            external_url = profile_data["external_url"]
            external_url_feature = int(bool(external_url))
        else:
            external_url_feature = None

        features = {}

        features["profile pic"] = (
            int(has_profile_picture)
            if has_profile_picture is not None else None
        )

        features["nums/length username"] = (
            sum(char.isdigit() for char in username) / len(username)
        )

        features["fullname words"] = (
            len(full_name.split())
            if isinstance(full_name, str) and full_name.strip()
            else None
        )

        features["nums/length fullname"] = (
            sum(char.isdigit() for char in full_name) / len(full_name)
            if isinstance(full_name, str) and full_name.strip()
            else None
        )

        features["name==username"] = (
            int(full_name.strip().lower() == username.lower())
            if isinstance(full_name, str) and full_name.strip()
            else None
        )

        features["description length"] = (
            len(biography)
            if isinstance(biography, str)
            else None
        )

        features["external URL"] = external_url_feature

        features["private"] = (
            int(is_private)
            if is_private is not None else None
        )

        features["#posts"] = posts
        features["#followers"] = followers
        features["#follows"] = following

        missing_features = [
            name
            for name, value in features.items()
            if value is None
        ]

        return {
            "platform": "instagram",
            "username": username,
            "profile_url": profile["profile_url"],
            "features": features,
            "missing_features": missing_features,
            "collection_status": (
                "complete"
                if not missing_features
                else "incomplete"
            ),
            "message": (
                "All profile features are available."
                if not missing_features
                else "Some profile information is unavailable."
            )
        }


if __name__ == "__main__":

    collector = ProfileDataCollector()

    test_url = "https://www.instagram.com/sunflower_demo/"

    sample_data = {
        "full_name": "Sunflower Demo",
        "biography": "Photography and lifestyle",
        "external_url": None,
        "has_profile_picture": True,
        "is_private": False,
        "posts": 25,
        "followers": 300,
        "following": 250
    }

    try:
        result = collector.collect_profile_data(
            test_url,
            sample_data
        )

        print("\nUPDATED PROFILE DATA COLLECTOR")
        print("=" * 45)

        print("Username:", result["username"])

        print("\nEXTRACTED FEATURES")

        for name, value in result["features"].items():
            print(f"{name}: {value}")

        print("\nCollection Status:", result["collection_status"])
        print("Missing Features:", result["missing_features"])
        print("Message:", result["message"])

    except ValueError as error:
        print("Error:", error)