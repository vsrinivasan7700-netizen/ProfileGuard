from m1_detector import predict_profile

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
    result = predict_profile(sample_profile)

    print("=" * 40)
    print("FAKE PROFILE DETECTION TEST")
    print("=" * 40)

    for key, value in result.items():
        print(f"{key}: {value}")

except Exception as error:
    print("Test failed:", error)

