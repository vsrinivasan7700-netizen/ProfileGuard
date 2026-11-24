from m1.instagram_collector import InstagramCollector


class DataSourceManager:

    def __init__(self):
        self.instagram = InstagramCollector()

    def get_profile_data(self, profile_url, user_data=None):

        # 1. Validate Instagram URL
        profile = self.instagram.collect_profile(profile_url)

        # 2. Validate supplied data
        if user_data is None:
            user_data = {}

        if not isinstance(user_data, dict):
            raise ValueError("Profile data must be a dictionary.")

        # 3. Define required profile information
        required_fields = [
            "full_name",
            "biography",
            "external_url",
            "has_profile_picture",
            "is_private",
            "posts",
            "followers",
            "following"
        ]

        # 4. Identify available and missing information
        available_data = {}
        missing_fields = []

        for field in required_fields:

            if field in user_data:
                available_data[field] = user_data[field]
            else:
                missing_fields.append(field)

        # 5. Return structured information
        return {
            "platform": "instagram",
            "username": profile["username"],
            "profile_url": profile["profile_url"],
            "profile_data": available_data,
            "data_source": "user_provided",
            "available_fields": list(available_data.keys()),
            "missing_fields": missing_fields,
            "collection_status": (
                "complete"
                if not missing_fields
                else "incomplete"
            )
        }


if __name__ == "__main__":

    manager = DataSourceManager()

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

        result = manager.get_profile_data(
            test_url,
            sample_data
        )

        print("\nDATA SOURCE MANAGER")
        print("=" * 45)

        print("Platform:", result["platform"])
        print("Username:", result["username"])
        print("Data Source:", result["data_source"])

        print("\nAVAILABLE FIELDS")

        for field in result["available_fields"]:
            print(field)

        print("\nMISSING FIELDS:", result["missing_fields"])

        print("Collection Status:", result["collection_status"])

        print("\nData source manager executed successfully!")

    except ValueError as error:
        print("Error:", error)