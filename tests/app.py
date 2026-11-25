import os
import sys
import json
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
    static_folder=str(PROJECT_ROOT / "static"),
    static_url_path="/static"
)


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db_connection():
    load_dotenv()

    # Railway production database settings
    db_host = os.getenv("MYSQLHOST", "localhost")
    db_port = int(os.getenv("MYSQLPORT", "3306"))
    db_user = os.getenv("MYSQLUSER", "root")
    db_password = (
        os.getenv("MYSQLPASSWORD")
        or os.getenv("MYSQL_PASSWORD")
    )
    db_name = (
        os.getenv("MYSQLDATABASE")
        or os.getenv("MYSQL_DATABASE")
        or "fake_profile_detection"
    )

    if not db_password:
        raise RuntimeError("MySQL password is not configured.")

    return pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )

# ==========================================================
# SAVE ANALYSIS RESULT TO MYSQL
# ==========================================================

def save_analysis_to_database(result, blockchain_info):

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            platform = result["platform"]
            username = result["username"]
            profile_url = result["profile_url"]

            # STEP 1: Find an existing profile.
            cursor.execute(
                """
                SELECT id
                FROM profiles
                WHERE platform = %s
                AND (
                    platform_user_id = %s
                    OR TRIM(TRAILING '/' FROM profile_url)
                       = TRIM(TRAILING '/' FROM %s)
                )
                LIMIT 1
                """,
                (platform, username, profile_url)
            )

            profile = cursor.fetchone()

            # STEP 2: Create profile if it does not exist.
            if profile is None:

                cursor.execute(
                    """
                    INSERT INTO profiles
                    (
                        platform,
                        profile_url,
                        platform_user_id
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (platform, profile_url, username)
                )

                profile_id = cursor.lastrowid

            else:

                profile_id = profile["id"]

            # STEP 3: Get prediction information.
            prediction = result["prediction"]

            fake_probability = float(
                prediction["fake_label_probability"]
            )

            risk_score = round(fake_probability * 100, 2)

            # STEP 4: Assign project risk category.
            if risk_score < 30:

                risk_category = "Low"

            elif risk_score < 70:

                risk_category = "Medium"

            else:

                risk_category = "High"

            # STEP 5: Prepare explanation JSON.
            explanation = {

                "predicted_label": prediction["predicted_label"],

                "prediction": prediction["prediction"],

                "fake_label_probability": fake_probability,

                "features": result["features"],

                "data_source": result["data_source"],

                "blockchain_index": blockchain_info["block_index"],

                "blockchain_hash": blockchain_info["block_hash"],

                "risk_score": risk_score,

                "risk_category": risk_category
            }

            # STEP 6: Insert analysis into MySQL.
            cursor.execute(
                """
                INSERT INTO analysis_results
                (
                    profile_id,
                    risk_score,
                    risk_category,
                    explanation,
                    model_version
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    profile_id,
                    risk_score,
                    risk_category,
                    json.dumps(explanation),
                    "random_forest_v1"
                )
            )

            analysis_id = cursor.lastrowid

        connection.commit()

        return {

            "analysis_id": analysis_id,

            "profile_id": profile_id,

            "risk_score": risk_score,

            "risk_category": risk_category
        }

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


# ==========================================================
# HOME ENDPOINT
# ==========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "message": "Blockchain-Based Fake Profile Detection API",

        "status": "running"
    })


# ==========================================================
# WEB DASHBOARD
# ==========================================================

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Display analysis totals and the latest saved analysis records."""
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM analysis_results")
            total_analyses = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT risk_category, COUNT(*) AS total
                FROM analysis_results
                GROUP BY risk_category
            """)
            rows = cursor.fetchall()

            risk_counts = {"Low": 0, "Medium": 0, "High": 0}
            for row in rows:
                category = row["risk_category"]
                if category in risk_counts:
                    risk_counts[category] = row["total"]

            cursor.execute("""
                SELECT
                    ar.id,
                    p.platform,
                    p.platform_user_id,
                    ar.risk_score,
                    ar.risk_category,
                    ar.analyzed_at
                FROM analysis_results AS ar
                INNER JOIN profiles AS p ON p.id = ar.profile_id
                ORDER BY ar.analyzed_at DESC
                LIMIT 10
            """)
            recent_records = cursor.fetchall()

        for record in recent_records:
            if record.get("analyzed_at") is not None:
                record["analyzed_at"] = record["analyzed_at"].strftime(
                    "%d %b %Y, %I:%M %p"
                )

        return render_template(
            "dashboard.html",
            total_profiles=total_analyses,
            total_analyses=total_analyses,
            risk_counts=risk_counts,
            recent_records=recent_records
        )

    except Exception:
        app.logger.exception("Dashboard loading failed")
        return "Unable to load dashboard. Check the Flask terminal for details.", 500

    finally:
        if connection is not None:
            connection.close()


# ==========================================================
# DATABASE HEALTH CHECK
# ==========================================================

@app.route("/api/health", methods=["GET"])
def health():

    connection = None

    try:

        connection = get_db_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT DATABASE() AS database_name"
            )

            database = cursor.fetchone()

            cursor.execute("SHOW TABLES")

            tables = cursor.fetchall()

        return jsonify({

            "status": "healthy",

            "database": database["database_name"],

            "tables": [
                list(table.values())[0]
                for table in tables
            ]

        })

    except (pymysql.MySQLError, RuntimeError):

        app.logger.exception("Database health check failed")

        return jsonify({

            "status": "error",

            "message": "Database connection failed."

        }), 500

    finally:

        if connection is not None:
            connection.close()


# ==========================================================
# DUPLICATE PROFILE DETECTION
# ==========================================================

@app.route("/api/detect-duplicate", methods=["POST"])
def detect_duplicate():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object."
        }), 400

    platform = data.get("platform")
    profile_url = data.get("profile_url")

    if not isinstance(platform, str) or not platform.strip():

        return jsonify({
            "status": "error",
            "message": "A valid platform is required."
        }), 400

    if not isinstance(profile_url, str) or not profile_url.strip():

        return jsonify({
            "status": "error",
            "message": "A valid profile_url is required."
        }), 400

    try:

        from m1.database_duplicate_detector import (
            find_duplicate_profiles
        )

        matches = find_duplicate_profiles({

            "platform": platform,

            "profile_url": profile_url

        })

        return jsonify({

            "status": "success",

            "platform": platform.strip().casefold(),

            "matches_found": len(matches),

            "matches": matches,

            "detection_method": "exact_normalized_url_match",

            "notice": (
                "A matching URL does not by itself prove "
                "that a profile is fake."
            )

        })

    except Exception:

        app.logger.exception("Duplicate detection failed")

        return jsonify({

            "status": "error",

            "message": "Duplicate detection could not be completed."

        }), 500


# ==========================================================
# MACHINE LEARNING PREDICTION HELPER
# ==========================================================

def get_profile_prediction(features):

    from m1.m1_detector import predict_profile

    return predict_profile(features)


# ==========================================================
# MACHINE LEARNING PREDICTION ENDPOINT
# ==========================================================

@app.route("/api/predict-profile", methods=["POST"])
def predict_profile_endpoint():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object."
        }), 400

    features = data.get("features", data)

    if not isinstance(features, dict):

        return jsonify({
            "status": "error",
            "message": "'features' must be a JSON object."
        }), 400

    try:

        result = get_profile_prediction(features)

        return jsonify({

            "status": "success",

            "detection_method": "random_forest",

            **result

        }), 200

    except ValueError as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:

        app.logger.exception("ML prediction failed")

        return jsonify({
            "status": "error",
            "message": "ML prediction could not be completed."
        }), 500


# ==========================================================
# ML PREDICTION + BLOCKCHAIN RECORDING
# ==========================================================

@app.route("/api/analyze-profile", methods=["POST"])
def analyze_profile():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object."
        }), 400

    platform = data.get("platform")
    profile_url = data.get("profile_url")
    features = data.get("features")

    if not isinstance(platform, str) or not platform.strip():

        return jsonify({
            "status": "error",
            "message": "A valid platform is required."
        }), 400

    if not isinstance(profile_url, str) or not profile_url.strip():

        return jsonify({
            "status": "error",
            "message": "A valid profile_url is required."
        }), 400

    if not isinstance(features, dict):

        return jsonify({
            "status": "error",
            "message": "'features' must be a JSON object."
        }), 400

    try:

        prediction = get_profile_prediction(features)

        record = {

            "event": "profile_analysis",

            "platform": platform.strip().casefold(),

            "profile_url": profile_url.strip(),

            "detection_method": "random_forest",

            "predicted_label": prediction["predicted_label"],

            "prediction": prediction["prediction"],

            "fake_label_probability": (
                prediction["fake_label_probability"]
            )
        }

        from blockchain.blockchain import Blockchain

        chain = Blockchain()

        block = chain.add_record(record)

        chain_valid = chain.is_chain_valid()

        if not chain_valid:

            return jsonify({
                "status": "error",
                "message": "Blockchain validation failed."
            }), 500

        return jsonify({

            "status": "success",

            "prediction": prediction,

            "blockchain": {

                "block_index": block.index,

                "timestamp": block.timestamp,

                "previous_hash": block.previous_hash,

                "block_hash": block.hash,

                "chain_valid": chain_valid
            }

        }), 200

    except ValueError as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:

        app.logger.exception("Combined profile analysis failed")

        return jsonify({
            "status": "error",
            "message": "Profile analysis could not be completed."
        }), 500


# ==========================================================
# COMPLETE ANALYSIS PIPELINE + MYSQL + BLOCKCHAIN
# ==========================================================

@app.route("/api/analyze-profile-pipeline", methods=["POST"])
def analyze_profile_pipeline():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object."
        }), 400

    profile_url = data.get("profile_url")

    profile_data = data.get("profile_data")

    if not isinstance(profile_url, str) or not profile_url.strip():

        return jsonify({
            "status": "error",
            "message": "A valid profile_url is required."
        }), 400

    if not isinstance(profile_data, dict):

        return jsonify({
            "status": "error",
            "message": "'profile_data' must be a JSON object."
        }), 400

    try:

        # STEP 1: Run complete analysis pipeline.
        from m1.complete_analysis_pipeline import (
            CompleteAnalysisPipeline
        )

        pipeline = CompleteAnalysisPipeline()

        result = pipeline.analyze(
            profile_url,
            profile_data
        )

        # STEP 2: Check data completeness.
        if result["status"] != "success":

            return jsonify(result), 422

        # STEP 3: Create blockchain record.
        from blockchain.blockchain import Blockchain

        chain = Blockchain()

        record = {

            "event": "profile_analysis",

            "platform": result["platform"],

            "username": result["username"],

            "profile_url": result["profile_url"],

            "data_source": result["data_source"],

            "predicted_label": (
                result["prediction"]["predicted_label"]
            ),

            "prediction": (
                result["prediction"]["prediction"]
            ),

            "fake_label_probability": (
                result["prediction"]["fake_label_probability"]
            )
        }

        block = chain.add_record(record)

        # STEP 4: Verify blockchain.
        chain_valid = chain.is_chain_valid()

        if not chain_valid:

            return jsonify({
                "status": "error",
                "message": "Blockchain validation failed."
            }), 500

        blockchain_info = {

            "block_index": block.index,

            "block_hash": block.hash,

            "chain_valid": chain_valid
        }

        # STEP 5: Save analysis into MySQL.
        database_result = save_analysis_to_database(
            result,
            blockchain_info
        )

        # STEP 6: Return final result.
        return jsonify({

            "status": "success",

            "profile_analysis": result,

            "database": {

                "saved": True,

                **database_result
            },

            "blockchain": blockchain_info,

            "notice": (
                "This prediction uses supplied profile information "
                "and reflects patterns in the training dataset. "
                "It does not prove account identity or authenticity."
            )

        }), 200

    except ValueError as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:

        app.logger.exception(
            "Complete profile analysis pipeline failed"
        )

        return jsonify({
            "status": "error",
            "message": "Complete profile analysis failed."
        }), 500


# ==========================================================
# ANALYSIS HISTORY
# ==========================================================

@app.route("/api/analysis-history", methods=["GET"])
def analysis_history():

    connection = None

    try:

        connection = get_db_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    ar.id AS analysis_id,
                    ar.profile_id,
                    p.platform,
                    p.profile_url,
                    p.platform_user_id,
                    ar.risk_score,
                    ar.risk_category,
                    ar.explanation,
                    ar.model_version,
                    ar.analyzed_at
                FROM analysis_results ar
                INNER JOIN profiles p
                    ON ar.profile_id = p.id
                ORDER BY ar.analyzed_at DESC
                LIMIT 100
                """
            )

            records = cursor.fetchall()

        # Convert database values into JSON-compatible values.
        for record in records:

            if record["analyzed_at"] is not None:

                record["analyzed_at"] = (
                    record["analyzed_at"].isoformat()
                )

            if isinstance(record["explanation"], str):

                try:
                    record["explanation"] = json.loads(
                        record["explanation"]
                    )
                except json.JSONDecodeError:
                    pass

        return jsonify({

            "status": "success",

            "total_records": len(records),

            "analysis_history": records

        }), 200

    except Exception:

        app.logger.exception("Analysis history retrieval failed")

        return jsonify({
            "status": "error",
            "message": "Could not retrieve analysis history."
        }), 500

    finally:

        if connection is not None:
            connection.close()


# ==========================================================
# BLOCKCHAIN VERIFICATION
# ==========================================================

@app.route("/api/blockchain/verify", methods=["GET"])
def verify_blockchain():

    try:

        from blockchain.blockchain import Blockchain

        chain = Blockchain()

        return jsonify({

            "status": "success",

            "chain_valid": chain.is_chain_valid(),

            "block_count": len(chain.chain),

            "latest_block_index": chain.get_latest_block().index

        }), 200

    except Exception:

        app.logger.exception("Blockchain verification failed")

        return jsonify({
            "status": "error",
            "message": "Blockchain verification failed."
        }), 500


# ==========================================================
# START FLASK APPLICATION
# ==========================================================
@app.route("/analyze")
def analyze_page():
    return render_template("analyze.html")

@app.route("/history")
def history_page():
    return render_template("history.html")

@app.route("/result", methods=["GET"])
def result_page():
    return render_template("result.html")

@app.route("/blockchain", methods=["GET"])
def blockchain_page():
    return render_template("blockchain.html")

if __name__ == "__main__":

    print("Starting Fake Profile Detection API...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
