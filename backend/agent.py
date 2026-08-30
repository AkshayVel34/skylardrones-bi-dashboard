import os
import json

from dotenv import load_dotenv
from google import genai

from analytics import (
    pipeline_analysis,
    revenue_analysis,
    billing_analysis,
    collection_analysis,
    leadership_summary,
    get_available_sectors,
    work_order_sector_analysis
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL = "gemini-3.6-flash"


# ============================================================
# FIND SECTOR
# ============================================================

def find_sector(question):

    question_lower = question.lower()

    available_sectors = get_available_sectors()

    for sector in available_sectors:

        if sector.lower() in question_lower:
            return sector

    return None


# ============================================================
# FIND REQUESTED UNKNOWN SECTOR
# ============================================================

def find_possible_sector(question):

    """
    Detect words that look like a sector even if they are
    not present in Monday.com.
    """

    question_lower = question.lower()

    available_sectors = get_available_sectors()

    # Known sector names should always take priority
    for sector in available_sectors:

        if sector.lower() in question_lower:
            return sector, True

    # Common sector names that may be requested but not present
    possible_sectors = [
        "energy",
        "healthcare",
        "automotive",
        "banking",
        "finance",
        "education",
        "oil",
        "gas",
        "telecom",
        "technology",
        "pharma",
        "agriculture"
    ]

    for sector in possible_sectors:

        if sector in question_lower:

            return sector.title(), False

    return None, None


# ============================================================
# GET BUSINESS DATA
# ============================================================

def get_business_data(question):

    question_lower = question.lower()

    sector = find_sector(question)

    requested_sector, sector_exists = find_possible_sector(
        question
    )


    # ========================================================
    # SECTOR PERFORMANCE
    # ========================================================

    if any(word in question_lower for word in [
        "sector",
        "industry",
        "performing",
        "performance"
    ]):

        # ----------------------------------------------------
        # EXISTING SECTOR
        # ----------------------------------------------------

        if sector:

            pipeline = pipeline_analysis(
                sector=sector
            )

            work_orders = work_order_sector_analysis(
                sector=sector
            )

            return {

                "query_type": "sector_performance",

                "sector": sector,

                "sector_exists": True,

                "pipeline": pipeline,

                "work_orders": work_orders,

                "available_sectors":
                    get_available_sectors()

            }


        # ----------------------------------------------------
        # UNKNOWN SECTOR
        # ----------------------------------------------------

        if requested_sector and not sector_exists:

            return {

                "query_type": "unknown_sector",

                "requested_sector":
                    requested_sector,

                "sector_exists": False,

                "available_sectors":
                    get_available_sectors()

            }


    # ========================================================
    # PIPELINE / DEALS
    # ========================================================

    if any(word in question_lower for word in [
        "pipeline",
        "deal",
        "deals",
        "sales"
    ]):

        if sector:

            pipeline = pipeline_analysis(
                sector=sector
            )

            work_orders = work_order_sector_analysis(
                sector=sector
            )

            return {

                "query_type":
                    "sector_pipeline",

                "sector":
                    sector,

                "pipeline":
                    pipeline,

                "work_orders":
                    work_orders,

                "available_sectors":
                    get_available_sectors()

            }

        else:

            return {

                "query_type":
                    "pipeline",

                "pipeline":
                    pipeline_analysis(),

                "available_sectors":
                    get_available_sectors()

            }


    # ========================================================
    # BILLING
    # ========================================================

    if any(word in question_lower for word in [
        "billing",
        "billed",
        "unbilled"
    ]):

        return {

            "query_type":
                "billing",

            "billing":
                billing_analysis()

        }


    # ========================================================
    # COLLECTIONS
    # ========================================================

    if any(word in question_lower for word in [
        "collection",
        "collected",
        "receivable",
        "receivables",
        "cash"
    ]):

        return {

            "query_type":
                "collections",

            "collections":
                collection_analysis()

        }


    # ========================================================
    # REVENUE
    # ========================================================

    if any(word in question_lower for word in [
        "revenue",
        "deal value",
        "total value"
    ]):

        return {

            "query_type":
                "revenue",

            "revenue":
                revenue_analysis()

        }


    # ========================================================
    # LEADERSHIP SUMMARY
    # ========================================================

    return {

        "query_type":
            "leadership",

        "summary":
            leadership_summary()

    }


# ============================================================
# GEMINI ANSWER
# ============================================================

def answer_question(question):

    business_data = get_business_data(
        question
    )

    data_json = json.dumps(
        business_data,
        indent=2,
        default=str
    )


    # ========================================================
    # SPECIAL CASE:
    # UNKNOWN SECTOR
    # ========================================================

    if business_data.get("query_type") == "unknown_sector":

        requested_sector = business_data.get(
            "requested_sector"
        )

        available = business_data.get(
            "available_sectors",
            []
        )

        return (
            f"**{requested_sector} is not currently present "
            f"as a sector in the Monday.com data.**\n\n"
            f"Available sectors are:\n"
            f"{', '.join(available)}\n\n"
            f"I cannot provide {requested_sector}-specific "
            f"performance figures without inventing data."
        )


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

    prompt = f"""
You are a Founder-level Business Intelligence Assistant.

You answer business questions using LIVE business data
retrieved dynamically from Monday.com.

USER QUESTION:
{question}

DATA RETRIEVED FROM MONDAY.COM:
{data_json}


============================================================
IMPORTANT INSTRUCTIONS
============================================================

1. The analytics data above is the SOURCE OF TRUTH.

2. NEVER invent numbers, sectors, dates, probabilities,
   revenue, pipeline values, or business facts.

3. If the data contains a sector-specific result,
   ALWAYS use that result.

4. NEVER claim that sector data is unavailable if the
   provided data contains a sector-specific result.

5. If the requested sector does not exist, clearly state
   that the sector is not present.

6. NEVER substitute company-wide data for an unavailable
   sector.

7. If a requested sector is unavailable, do not provide
   unrelated company-wide performance numbers unless the
   user explicitly asks for overall company performance.

8. Missing values must NOT be treated as zero unless the
   analytics result explicitly says they are zero.

9. If deal values are missing, clearly mention that the
   reported pipeline is based only on available deal values.

10. Deal probability data is currently missing. Therefore,
    weighted pipeline forecasting cannot be calculated
    reliably.

11. Work-order monetary values are in Indian Rupees.

12. ALWAYS use the ₹ symbol for monetary values.

13. NEVER use "$" or "USD".

14. Convert large numbers into readable executive format.

Examples:

2305518040 -> ₹2.31B

109255888 -> ₹109.26M

126719936 -> ₹126.72M

36291748 -> ₹36.29M


============================================================
ANSWER FORMAT
============================================================

Start with a short DIRECT ANSWER.

Then provide only the most useful information.

For normal business questions:

**Direct Answer**

1-3 sentence answer.

**Key Numbers**
- Important metric
- Important metric
- Important metric

**Insight**
One or two useful business observations.

**Data Quality**
Mention important missing or incomplete data.


For sector questions:

**Direct Answer**

State the actual sector-specific performance.

Include:
- Deal count
- Pipeline value
- Important stages
- Work-order information if available

Then mention relevant data-quality limitations.


For unavailable sectors:

Clearly say the sector is not present.

List available sectors.

Do NOT substitute overall company numbers.


For leadership-update questions:

Provide a SHORT executive briefing containing:

**Executive Summary**

**Key Numbers**
- Pipeline
- Work orders
- Billing
- Collections

**Opportunities**
1-2 points

**Risks**
1-2 points

**Data Quality**
Important limitations only.


============================================================
STYLE
============================================================

- Concise
- Executive-friendly
- Clear
- Evidence-based
- No unnecessary explanation
- No fabricated information
- Use ₹
- Use bullet points
- Do not overwhelm the founder with raw data
"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text


    except Exception as e:

        return (
            "The Monday.com business data was retrieved "
            "successfully, but the AI response could not "
            "be generated.\n\n"
            f"API error: {str(e)}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GEMINI BUSINESS INTELLIGENCE AGENT")
    print("=" * 60)


    test_questions = [

        "What is our total pipeline value?",

        "How much has been billed?",

        "How much money is receivable?",

        "How is the Renewables sector performing?",

        "How is the Energy sector performing?",

        "Give me a short leadership update."

    ]


    for question in test_questions:

        print("\nQUESTION:")
        print(question)

        print("\nANSWER:")

        print(
            answer_question(question)
        )

        print("\n" + "-" * 60)