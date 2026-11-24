class ProfileFeatureExtractor:

    FEATURE_NAMES = [
        "profile pic",
        "nums/length username",
        "fullname words",
        "nums/length fullname",
        "name==username",
        "description length",
        "external URL",
        "private",
        "#posts",
        "#followers",
        "#follows"
    ]

    NUMERIC_FEATURES = [
        "nums/length username",
        "fullname words",
        "nums/length fullname",
        "description length",
        "#posts",
        "#followers",
        "#follows"
    ]

    BOOLEAN_FEATURES = [
        "profile pic",
        "name==username",
        "external URL",
        "private"
    ]

    def extract_features(self, profile_data):

        if not isinstance(profile_data, dict):
            raise ValueError("Profile data must be a dictionary.")

        features = {}

        for feature in self.NUMERIC_FEATURES:

            if feature not in profile_data:
                raise ValueError(f"Missing feature: {feature}")

            try:
                value = float(profile_data[feature])
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numeric value: {feature}")

            if value < 0:
                raise ValueError(f"{feature} cannot be negative.")

            features[feature] = value

        for feature in self.BOOLEAN_FEATURES:

            if feature not in profile_data:
                raise ValueError(f"Missing feature: {feature}")

            value = profile_data[feature]

            if value not in (0, 1, True, False):
                raise ValueError(
                    f"{feature} must be 0 or 1."
                )

            features[feature] = int(value)

        # Arrange features in the exact training order.
        ordered_features = {
            name: features[name]
            for name in self.FEATURE_NAMES
        }

        return ordered_features


if __name__ == "__main__":

    extractor = ProfileFeatureExtractor()

    sample_profile = {
        "profile pic": 1,
        "nums/length username": 0.0,
        "fullname words": 2,
        "nums/length fullname": 0.0,
        "name==username": 0,
        "description length": 50,
        "external URL": 0,
        "private": 0,
        "#posts": 25,
        "#followers": 300,
        "#follows": 250
    }

    try:
        result = extractor.extract_features(sample_profile)

        print("\nPROFILE FEATURE EXTRACTION")
        print("=" * 40)

        for feature, value in result.items():
            print(f"{feature}: {value}")

        print("\nFeature extraction successful!")

    except ValueError as error:
        print("Error:", error)