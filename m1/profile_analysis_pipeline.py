from m1.instagram_collector import InstagramCollector
from m1.profile_feature_extractor import ProfileFeatureExtractor
from m1.m1_detector import predict_profile


class ProfileAnalysisPipeline:

    def __init__(self):
        self.collector = InstagramCollector()
        self.extractor = ProfileFeatureExtractor()

    def analyze_profile(self, profile_url, profile_data):

        # Step 1: Validate Instagram URL
        profile = self.collector.collect_profile(profile_url)

        # Step 2: Validate and arrange ML features
        features = self.extractor.extract_features(profile_data)

        # Step 3: Run Random Forest prediction
        prediction = predict_profile(features)

        # Step 4: Prepare final result
        result = {
            "platform": profile["platform"],
            "username": profile["username"],
            "profile_url": profile["profile_url"],
            "features": features,
            "prediction": prediction,
            "status": "success"
        }

        return result


if __name__ == "__main__":

    pipeline = ProfileAnalysisPipeline()

    sample_url = "https://www.instagram.com/sunflower_demo/"

    # Demo values only; these are not collected from Instagram.
    sample_profile_data = {
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
        result = pipeline.analyze_profile(
            sample_url,
            sample_profile_data
        )

        print("\nPROFILE ANALYSIS PIPELINE")
        print("=" * 45)

        print("Platform:", result["platform"])
        print("Username:", result["username"])
        print("Profile URL:", result["profile_url"])

        print("\nMACHINE LEARNING RESULT")
        print("-" * 45)

        for key, value in result["prediction"].items():
            print(f"{key}: {value}")

        print("\nPipeline execution successful!")

    except (ValueError, TypeError, KeyError) as error:
        print("Analysis error:", error)
