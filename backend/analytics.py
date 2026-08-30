from monday_data import get_deals, get_work_orders


# ============================================================
# DEALS COLUMN IDS
# ============================================================

DEAL_STATUS = "color_mm6qx7wa"
CLOSE_DATE = "date_mm6qhzzg"
CLOSURE_PROBABILITY = "text_mm6qzz8w"
DEAL_VALUE = "numeric_mm6qchpc"
TENTATIVE_CLOSE_DATE = "date_mm6q3tcn"
DEAL_STAGE = "color_mm6q5adx"
SECTOR = "text_mm6qck2e"


# ============================================================
# WORK ORDER COLUMN IDS
# ============================================================

WO_SECTOR = "text_mm6q1nvv"

AMOUNT_INCL_GST = "numeric_mm6qj14z"
BILLED_INCL_GST = "numeric_mm6qjtpw"
COLLECTED_AMOUNT = "numeric_mm6qe49h"
AMOUNT_RECEIVABLE = "numeric_mm6qjn8v"

EXECUTION_STATUS = "color_mm6qk3ak"
INVOICE_STATUS = "color_mm6qk7p6"
BILLING_STATUS = "color_mm6qwc0v"
WO_STATUS = "color_mm6qpptf"


# ============================================================
# HELPER: GET COLUMN VALUE
# ============================================================

def get_value(item, column_id):
    """
    Return the displayed text value of a Monday.com column.
    """

    for column in item.get("column_values", []):

        if column.get("id") == column_id:

            value = column.get("text")

            if value is not None:
                return value

            return ""

    return ""


# ============================================================
# HELPER: NORMALIZE TEXT
# ============================================================

def normalize_text(value):

    if value is None:
        return ""

    return str(value).strip().lower()


# ============================================================
# HELPER: NORMALIZE SECTOR
# ============================================================

def normalize_sector(value):

    value = normalize_text(value)

    # Ignore empty values
    if not value:
        return ""

    # Ignore imported column-header values
    if value in [
        "sector/service",
        "sector",
        "sector service"
    ]:
        return ""

    return value


# ============================================================
# HELPER: TEXT SEARCH
# ============================================================

def contains_text(value, search):

    return normalize_text(search) in normalize_text(value)


# ============================================================
# HELPER: CLEAN NUMBER
# ============================================================

def clean_number(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("$", "")
    value = value.replace("%", "")

    try:

        return float(value)

    except (ValueError, TypeError):

        return None


# ============================================================
# HELPER: CLEAN PROBABILITY
# ============================================================

def clean_probability(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace("%", "").strip()

    try:

        probability = float(value)

        # Example:
        # 75 -> 0.75
        if probability > 1:
            probability = probability / 100

        # Invalid probability
        if probability < 0 or probability > 1:
            return None

        return probability

    except (ValueError, TypeError):

        return None


# ============================================================
# HELPER: FORMAT CURRENCY
# ============================================================

def format_currency(value):

    if value is None:
        return "₹0"

    value = float(value)

    if abs(value) >= 1_000_000_000:

        return f"₹{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:

        return f"₹{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:

        return f"₹{value / 1_000:.2f}K"

    return f"₹{value:.2f}"


# ============================================================
# 1. AVAILABLE SECTORS
# ============================================================

def get_available_sectors():

    deals = get_deals()

    sectors = set()

    for deal in deals:

        value = normalize_sector(
            get_value(deal, SECTOR)
        )

        if value:

            sectors.add(value)

    # Return original-looking names
    result = []

    for sector in sorted(sectors):

        result.append(sector.title())

    return result


# ============================================================
# 2. PIPELINE ANALYSIS
# ============================================================

def pipeline_analysis(
    sector=None,
    quarter=None,
    year=None
):

    deals = get_deals()

    filtered = deals

    # --------------------------------------------------------
    # SECTOR FILTER
    # --------------------------------------------------------

    if sector:

        sector_normalized = normalize_text(
            sector
        )

        filtered = [

            deal for deal in deals

            if normalize_sector(
                get_value(deal, SECTOR)
            ) == sector_normalized

        ]

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    total_pipeline_value = 0

    weighted_pipeline_value = 0

    valid_values = 0

    missing_values = 0

    valid_probability = 0

    missing_probability = 0

    stage_summary = {}

    # --------------------------------------------------------
    # PROCESS DEALS
    # --------------------------------------------------------

    for deal in filtered:

        # Deal value
        value = clean_number(
            get_value(
                deal,
                DEAL_VALUE
            )
        )

        if value is None:

            missing_values += 1

        else:

            total_pipeline_value += value

            valid_values += 1

        # Probability
        probability = clean_probability(
            get_value(
                deal,
                CLOSURE_PROBABILITY
            )
        )

        if probability is None:

            missing_probability += 1

        else:

            valid_probability += 1

            if value is not None:

                weighted_pipeline_value += (
                    value * probability
                )

        # Stage
        stage = get_value(
            deal,
            DEAL_STAGE
        )

        stage = stage.strip()

        if not stage:

            stage = "Unknown"

        stage_summary[stage] = (
            stage_summary.get(stage, 0) + 1
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "sector":
            sector or "All sectors",

        "deal_count":
            len(filtered),

        "total_pipeline_value":
            total_pipeline_value,

        "weighted_pipeline_value":
            weighted_pipeline_value,

        "stage_breakdown":
            stage_summary,

        "data_quality": {

            "valid_value_records":
                valid_values,

            "missing_values":
                missing_values,

            "valid_probability":
                valid_probability,

            "missing_probability":
                missing_probability

        }

    }


# ============================================================
# 3. REVENUE / DEAL VALUE ANALYSIS
# ============================================================

def revenue_analysis():

    deals = get_deals()

    total = 0

    valid_records = 0

    missing_values = 0

    for deal in deals:

        value = clean_number(
            get_value(
                deal,
                DEAL_VALUE
            )
        )

        if value is None:

            missing_values += 1

        else:

            total += value

            valid_records += 1

    return {

        "total_deal_value":
            total,

        "total_deal_value_formatted":
            format_currency(total),

        "total_deals":
            len(deals),

        "valid_value_records":
            valid_records,

        "missing_value_records":
            missing_values

    }


# ============================================================
# 4. BILLING ANALYSIS
# ============================================================

def billing_analysis():

    work_orders = get_work_orders()

    total_amount = 0

    total_billed = 0

    missing_amount = 0

    missing_billed = 0

    for wo in work_orders:

        amount = clean_number(
            get_value(
                wo,
                AMOUNT_INCL_GST
            )
        )

        billed = clean_number(
            get_value(
                wo,
                BILLED_INCL_GST
            )
        )

        if amount is None:

            missing_amount += 1

        else:

            total_amount += amount

        if billed is None:

            missing_billed += 1

        else:

            total_billed += billed

    total_unbilled = (
        total_amount - total_billed
    )

    if total_amount > 0:

        billing_percentage = (
            total_billed /
            total_amount
        ) * 100

    else:

        billing_percentage = 0

    return {

        "work_orders":
            len(work_orders),

        "total_order_value":
            total_amount,

        "total_billed":
            total_billed,

        "total_unbilled":
            total_unbilled,

        "billing_percentage":
            billing_percentage,

        "data_quality": {

            "missing_amount":
                missing_amount,

            "missing_billed":
                missing_billed

        }

    }


# ============================================================
# 5. COLLECTION ANALYSIS
# ============================================================

def collection_analysis():

    work_orders = get_work_orders()

    total_collected = 0

    total_receivable = 0

    missing_collected = 0

    missing_receivable = 0

    for wo in work_orders:

        collected = clean_number(
            get_value(
                wo,
                COLLECTED_AMOUNT
            )
        )

        receivable = clean_number(
            get_value(
                wo,
                AMOUNT_RECEIVABLE
            )
        )

        if collected is None:

            missing_collected += 1

        else:

            total_collected += collected

        if receivable is None:

            missing_receivable += 1

        else:

            total_receivable += receivable

    return {

        "total_collected":
            total_collected,

        "total_receivable":
            total_receivable,

        "data_quality": {

            "missing_collected":
                missing_collected,

            "missing_receivable":
                missing_receivable

        }

    }


# ============================================================
# 6. WORK ORDER SECTOR ANALYSIS
# ============================================================

def work_order_sector_analysis(
    sector=None
):

    work_orders = get_work_orders()

    if sector:

        sector_normalized = normalize_text(
            sector
        )

        filtered = [

            wo for wo in work_orders

            if normalize_sector(
                get_value(
                    wo,
                    WO_SECTOR
                )
            ) == sector_normalized

        ]

    else:

        filtered = work_orders

    total_order_value = 0

    total_billed = 0

    total_collected = 0

    total_receivable = 0

    missing_amount = 0

    missing_billed = 0

    missing_collected = 0

    missing_receivable = 0

    for wo in filtered:

        amount = clean_number(
            get_value(
                wo,
                AMOUNT_INCL_GST
            )
        )

        billed = clean_number(
            get_value(
                wo,
                BILLED_INCL_GST
            )
        )

        collected = clean_number(
            get_value(
                wo,
                COLLECTED_AMOUNT
            )
        )

        receivable = clean_number(
            get_value(
                wo,
                AMOUNT_RECEIVABLE
            )
        )

        if amount is None:

            missing_amount += 1

        else:

            total_order_value += amount

        if billed is None:

            missing_billed += 1

        else:

            total_billed += billed

        if collected is None:

            missing_collected += 1

        else:

            total_collected += collected

        if receivable is None:

            missing_receivable += 1

        else:

            total_receivable += receivable

    if total_order_value > 0:

        billing_percentage = (
            total_billed /
            total_order_value
        ) * 100

    else:

        billing_percentage = 0

    return {

        "sector":
            sector or "All sectors",

        "work_orders":
            len(filtered),

        "total_order_value":
            total_order_value,

        "total_billed":
            total_billed,

        "total_collected":
            total_collected,

        "total_receivable":
            total_receivable,

        "billing_percentage":
            billing_percentage,

        "data_quality": {

            "missing_amount":
                missing_amount,

            "missing_billed":
                missing_billed,

            "missing_collected":
                missing_collected,

            "missing_receivable":
                missing_receivable

        }

    }


# ============================================================
# 7. LEADERSHIP SUMMARY
# ============================================================

def leadership_summary():

    pipeline = pipeline_analysis()

    revenue = revenue_analysis()

    billing = billing_analysis()

    collections = collection_analysis()

    return {

        "pipeline": pipeline,

        "revenue": revenue,

        "billing": billing,

        "collections": collections,

        "data_quality": {

            "deals_missing_value":
                revenue[
                    "missing_value_records"
                ],

            "deals_missing_probability":
                pipeline[
                    "data_quality"
                ][
                    "missing_probability"
                ],

            "work_orders_missing_receivable":
                collections[
                    "data_quality"
                ][
                    "missing_receivable"
                ]

        }

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print("AVAILABLE SECTORS")

    print("-" * 60)

    print(
        get_available_sectors()
    )


    print("\n" + "=" * 60)

    print("PIPELINE")

    print("-" * 60)

    print(
        pipeline_analysis()
    )


    print("\n" + "=" * 60)

    print("RENEWABLES PIPELINE")

    print("-" * 60)

    print(
        pipeline_analysis(
            sector="Renewables"
        )
    )


    print("\n" + "=" * 60)

    print("REVENUE")

    print("-" * 60)

    print(
        revenue_analysis()
    )


    print("\n" + "=" * 60)

    print("BILLING")

    print("-" * 60)

    print(
        billing_analysis()
    )


    print("\n" + "=" * 60)

    print("COLLECTIONS")

    print("-" * 60)

    print(
        collection_analysis()
    )


    print("\n" + "=" * 60)

    print("LEADERSHIP SUMMARY")

    print("-" * 60)

    print(
        leadership_summary()
    )