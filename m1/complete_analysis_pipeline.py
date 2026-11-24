from m1.data_source_manager import DataSourceManager
from m1.profile_data_collector import ProfileDataCollector
from m1.m1_detector import predict_profile


class CompleteAnalysisPipeline:

    def __init__(self):
        self.data_manager = DataSourceManager()
        self.data_collector = ProfileDataCollector()

    def analyze(self, profile_url, user_data):

        # STEP 1: Identify the profile and data source
        source_result = self.data_manager.get_profile_data(
            profile_url,
            user_data
        )

        # STEP 2: Process profile information
        collection_result = self.data_collector.collect_profile_data(
            profile_url,
            source_result["profile_data"]
        )

        # STEP 3: Check missing features
        if collection_result["missing_features"]:

            return {
                "status": "incomplete",
                "username": collection_result["username"],
                "missing_features": collection_result["missing_features"],
                "message": "Insufficient profile information for prediction."
            }

        # STEP 4: Run machine learning prediction
        prediction_result = predict_profile(
            collection_result["features"]
        )

        # STEP 5: Prepare final analysis
        return {
            "status": "success",
            "platform": "instagram",
            "username": collection_result["username"],
            "profile_url": collection_result["profile_url"],
            "data_source": source_result["data_source"],
            "features": collection_result["features"],
            "prediction": prediction_result,
            "message": "Profile analysis completed successfully."
        }


if __name__ == "__main__":

    pipeline = CompleteAnalysisPipeline()

    test_url = "https://www.instagram.com/sunflower_demo/"

    # Demonstration data only.
    # These values are NOT collected from Instagram.
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

        result = pipeline.analyze(
            test_url,
            sample_data
        )

        print("\nCOMPLETE PROFILE ANALYSIS")
        print("=" * 50)

        print("Status:", result["status"])
        print("Username:", result["username"])

        if result["status"] == "success":

            print("Platform:", result["platform"])
            print("Data Source:", result["data_source"])

            print("\nMACHINE LEARNING PREDICTION")
            print("-" * 50)

            for key, value in result["prediction"].items():
                print(f"{key}: {value}")

        else:

            print("Missing Features:", result["missing_features"])
            print("Message:", result["message"])

        print("\nAnalysis execution completed!")

    except (ValueError, TypeError, KeyError) as error:

        print("Analysis Error:", error)