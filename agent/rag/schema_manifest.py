"""
Schema manifest with per-view documents for ChromaDB RAG retrieval.
"""

PRIMARY_KEY_RULES = """PRIMARY KEY RULE: UWI (Unique Well Identifier) and UBHI (Unique Borehole Identifier)
refer to the same physical wellbore. Always join across views using UWI = UWI,
UBHI = UBHI, or UWI = UBHI interchangeably. V_WELL_HEADER exposes both columns.

ORACLE SQL RULES:
- Use FETCH FIRST n ROWS ONLY (not LIMIT)
- Use NVL() for null handling
- Use TO_DATE('2020-01-01','YYYY-MM-DD') for date literals
- Use EXTRACT(YEAR FROM col) for year
- Always prefix view names: welldata.V_VIEW_NAME
- Always qualify column names with alias when joining
"""

MINIMAL_SCHEMA = """=== AVAILABLE VIEWS (use only these) ===
welldata.V_WELL_HEADER - Well identity, location, operator, basin, dates, depth, status
welldata.V_PETROPHYSICS - Reservoir quality (porosity, permeability, saturation) per borehole
welldata.V_PRODUCTION_MONTHLY - Monthly oil, gas, water production per well
welldata.V_FORMATION_TOPS - Stratigraphic formation tops per well
welldata.V_WELL_SUMMARY - Aggregated lifetime stats per well
welldata.V_CORE_ANALYSIS - Lab core analysis per well
welldata.V_GAS_COMPOSITION - Gas compositional analysis per well
"""

VIEW_DOCUMENTS = [
    {
        "id": "V_WELL_HEADER",
        "text": "V_WELL_HEADER: Master well information. One row per well. Location, operator, basin, dates, depth, status. "
                "Columns: UWI (well identifier), UBHI (borehole alias), WELL_NAME, OPERATOR, COUNTRY (India), "
                "BASIN (Krishna-Godavari/Cambay/Rajasthan), FIELD_NAME, SPUD_DATE, COMPLETION_DATE, "
                "WELL_TYPE (EXPLORATION/DEVELOPMENT/APPRAISAL), WELL_STATUS (ACTIVE/ABANDONED/SUSPENDED), "
                "SURFACE_LAT, SURFACE_LON, TOTAL_DEPTH_M, KB_ELEVATION_M, DRILL_DURATION_MONTHS. "
                "Use for: well identity queries, location, operator, basin, dates, depth, status.",
        "metadata": {"view_name": "V_WELL_HEADER", "category": "well_identity"}
    },
    {
        "id": "V_PETROPHYSICS",
        "text": "V_PETROPHYSICS: Reservoir quality measurements per borehole at sampled depths. "
                "Columns: UBHI, UWI, BOREHOLE_TYPE (VERTICAL/DIRECTIONAL/HORIZONTAL), SAMPLE_DEPTH_M, "
                "POROSITY (fraction 0-1), PERMEABILITY (mD), WATER_SAT (fraction 0-1), "
                "OIL_SAT (1 - WATER_SAT), FORMATION, RESERVOIR_QUALITY (EXCELLENT/GOOD/FAIR/POOR). "
                "Use for: porosity, permeability, reservoir quality, formation properties.",
        "metadata": {"view_name": "V_PETROPHYSICS", "category": "reservoir"}
    },
    {
        "id": "V_PRODUCTION_MONTHLY",
        "text": "V_PRODUCTION_MONTHLY: Monthly oil, gas, and water production per well. "
                "Columns: UWI, WELL_NAME, OPERATOR, FIELD_NAME, PROD_DATE, PROD_YEAR, PROD_MONTH, "
                "OIL_BBL (barrels), GAS_MCF (thousand cubic feet), WATER_BBL, HOURS_ON, "
                "OIL_RATE_BOPD (barrels per operating day), GAS_RATE_MCFPD. "
                "Use for: production trends, top producing fields, cumulative volumes, rates.",
        "metadata": {"view_name": "V_PRODUCTION_MONTHLY", "category": "production"}
    },
    {
        "id": "V_FORMATION_TOPS",
        "text": "V_FORMATION_TOPS: Stratigraphic formation tops per well. "
                "Columns: UWI, WELL_NAME, BASIN, FORMATION, TOP_DEPTH_M, BASE_DEPTH_M, "
                "THICKNESS_M, LITHOLOGY (SANDSTONE/LIMESTONE/SHALE/DOLOMITE). "
                "Use for: formation depth, thickness, lithology, stratigraphic columns.",
        "metadata": {"view_name": "V_FORMATION_TOPS", "category": "geology"}
    },
    {
        "id": "V_WELL_SUMMARY",
        "text": "V_WELL_SUMMARY: Aggregated lifetime statistics per well. One row per well. "
                "Columns: UWI, WELL_NAME, OPERATOR, FIELD_NAME, WELL_TYPE, WELL_STATUS, SPUD_DATE, "
                "TOTAL_DEPTH_M, CUMULATIVE_OIL_BBL, CUMULATIVE_GAS_MCF, CUMULATIVE_WATER_BBL, "
                "PRODUCING_MONTHS, AVG_POROSITY, AVG_PERMEABILITY. "
                "Use for: best producing wells, operator rankings, performance comparison.",
        "metadata": {"view_name": "V_WELL_SUMMARY", "category": "summary"}
    },
    {
        "id": "V_CORE_ANALYSIS",
        "text": "V_CORE_ANALYSIS: Laboratory core analysis per well. "
                "Columns: UWI, WELL_NAME, FIELD_NAME, CORE_RUN, TOP_DEPTH_M, BASE_DEPTH_M, "
                "GRAIN_DENSITY (g/cc), BULK_DENSITY (g/cc), RECOVERY_PCT (0-100), "
                "COMPUTED_POROSITY (1 - bulk/grain). "
                "Use for: core recovery, density measurements, computed porosity.",
        "metadata": {"view_name": "V_CORE_ANALYSIS", "category": "core"}
    },
    {
        "id": "V_GAS_COMPOSITION",
        "text": "V_GAS_COMPOSITION: Natural gas compositional analysis per well. "
                "Columns: UWI, WELL_NAME, OPERATOR, FIELD_NAME, BASIN, SAMPLE_DATE, SAMPLE_YEAR, "
                "METHANE_PCT (75-92%), ETHANE_PCT, PROPANE_PCT, BUTANE_PCT, PENTANE_PCT, "
                "CO2_PCT, H2S_PCT (above 0.5% = SOUR), N2_PCT, HYDROCARBON_PCT, "
                "HEATING_VALUE_BTU, SPECIFIC_GRAVITY, SAMPLE_TYPE (WELLHEAD/SEPARATOR/PIPELINE), "
                "GAS_SWEETNESS (SOUR/SWEET), GAS_RICHNESS (RICH/LEAN/DRY). "
                "Use for: gas composition, sour gas, methane content, heating value.",
        "metadata": {"view_name": "V_GAS_COMPOSITION", "category": "gas"}
    },
]

VIEWS_LIST = [
    {"view_name": "V_WELL_HEADER", "description": "Master well information. One row per well. Location, operator, basin, dates, depth, status."},
    {"view_name": "V_PETROPHYSICS", "description": "Reservoir quality measurements per borehole at sampled depths. Porosity, permeability, water saturation."},
    {"view_name": "V_PRODUCTION_MONTHLY", "description": "Monthly oil, gas, and water production per well. Volumes, rates, trends."},
    {"view_name": "V_FORMATION_TOPS", "description": "Stratigraphic formation tops per well. Depth, thickness, lithology."},
    {"view_name": "V_WELL_SUMMARY", "description": "Aggregated lifetime statistics per well. Cumulative production, avg reservoir quality."},
    {"view_name": "V_CORE_ANALYSIS", "description": "Laboratory core analysis. Density, recovery, computed porosity."},
    {"view_name": "V_GAS_COMPOSITION", "description": "Natural gas compositional analysis. Methane, CO2, H2S, heating value, sweetness, richness."},
]

FULL_SCHEMA = f"""=== DATABASE SCHEMA ===

{PRIMARY_KEY_RULES}
""" + "\n".join(
    f"--- VIEW: welldata.{d['id']} ---\n"
    f"{d['text'][:d['text'].index(' Use for:')]}\n"
    f"Sample questions: {d['text'].split(' Use for:')[1].strip()}"
    for d in VIEW_DOCUMENTS
) + "\n\n=== END SCHEMA ==="


def get_view_schema(view_ids: list[str]) -> str:
    """Build schema string from a list of view IDs."""
    parts = [PRIMARY_KEY_RULES]
    for doc in VIEW_DOCUMENTS:
        if doc["id"] in view_ids:
            parts.append(f"--- VIEW: welldata.{doc['id']} ---\n{doc['text']}")
    return "\n".join(parts)


def get_schema_context(question: str = "") -> str:
    """
    Retrieves schema context for a question.
    Uses ChromaDB RAG when available, falls back to full schema.
    """
    from .retriever import retrieve_schema_context
    return retrieve_schema_context(question)
