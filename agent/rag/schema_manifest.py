VIEWS = [
    {
        "view_name": "V_WELL_HEADER",
        "description": (
            "Master well information. One row per well. "
            "Use for well metadata: location, operator, basin, field, dates, depth, status. "
            "Primary key is UWI. Also exposes UBHI as an alias of UWI for joins."
        ),
        "columns": [
            {"name": "UWI",          "type": "VARCHAR2", "description": "Unique Well Identifier. Primary key. 14-character alphanumeric."},
            {"name": "UBHI",         "type": "VARCHAR2", "description": "Alias of UWI. Use this when joining to views keyed on UBHI."},
            {"name": "WELL_NAME",    "type": "VARCHAR2", "description": "Human-readable well name, e.g. ONGC-KG-001."},
            {"name": "OPERATOR",     "type": "VARCHAR2", "description": "Company operating the well. Values: ONGC, Reliance, Cairn India."},
            {"name": "COUNTRY",      "type": "VARCHAR2", "description": "Always India in this dataset."},
            {"name": "BASIN",        "type": "VARCHAR2", "description": "Sedimentary basin. Values: Krishna-Godavari, Cambay, Rajasthan."},
            {"name": "FIELD_NAME",   "type": "VARCHAR2", "description": "Named oil/gas field within the basin."},
            {"name": "SPUD_DATE",    "type": "DATE",     "description": "Date drilling began."},
            {"name": "COMPLETION_DATE","type": "DATE",   "description": "Date drilling completed. NULL if still drilling."},
            {"name": "WELL_TYPE",    "type": "VARCHAR2", "description": "EXPLORATION, DEVELOPMENT, or APPRAISAL."},
            {"name": "WELL_STATUS",  "type": "VARCHAR2", "description": "ACTIVE, ABANDONED, or SUSPENDED."},
            {"name": "SURFACE_LAT",  "type": "NUMBER",   "description": "Surface latitude in decimal degrees."},
            {"name": "SURFACE_LON",  "type": "NUMBER",   "description": "Surface longitude in decimal degrees."},
            {"name": "TOTAL_DEPTH_M","type": "NUMBER",   "description": "Total drilled depth in metres."},
            {"name": "KB_ELEVATION_M","type": "NUMBER",  "description": "Kelly bushing elevation in metres above sea level."},
            {"name": "DRILL_DURATION_MONTHS","type": "NUMBER","description": "Months between spud and completion."},
        ],
        "join_keys": ["UWI", "UBHI"],
        "example_questions": [
            "How many wells did ONGC drill in the Krishna-Godavari basin?",
            "List all active wells drilled after 2015.",
            "What is the deepest well in the Cambay basin?",
        ]
    },
    {
        "view_name": "V_PETROPHYSICS",
        "description": (
            "Reservoir quality measurements per borehole at sampled depths. "
            "Use for porosity, permeability, water saturation, formation, and reservoir quality. "
            "Primary key is (UBHI, SAMPLE_DEPTH_M). Join to V_WELL_HEADER on UWI = UWI or UBHI = UBHI."
        ),
        "columns": [
            {"name": "UBHI",              "type": "VARCHAR2", "description": "Unique Borehole Identifier. Same entity as UWI."},
            {"name": "UWI",               "type": "VARCHAR2", "description": "Parent well identifier."},
            {"name": "BOREHOLE_TYPE",     "type": "VARCHAR2", "description": "VERTICAL, DIRECTIONAL, or HORIZONTAL."},
            {"name": "SAMPLE_DEPTH_M",    "type": "NUMBER",   "description": "Depth of measurement in metres."},
            {"name": "POROSITY",          "type": "NUMBER",   "description": "Fractional porosity (0 to 1). Multiply by 100 for percentage."},
            {"name": "PERMEABILITY",      "type": "NUMBER",   "description": "Permeability in millidarcies (mD)."},
            {"name": "WATER_SAT",         "type": "NUMBER",   "description": "Water saturation fraction (0 to 1)."},
            {"name": "OIL_SAT",           "type": "NUMBER",   "description": "Oil saturation = 1 - WATER_SAT."},
            {"name": "FORMATION",         "type": "VARCHAR2", "description": "Geological formation name at this depth."},
            {"name": "RESERVOIR_QUALITY", "type": "VARCHAR2", "description": "EXCELLENT (>20%), GOOD (12-20%), FAIR (5-12%), POOR (<5%)."},
        ],
        "join_keys": ["UBHI", "UWI"],
        "example_questions": [
            "What is the average porosity in the Rajahmundry formation?",
            "Show wells with permeability above 100 mD.",
            "Which borehole has the best reservoir quality?",
        ]
    },
    {
        "view_name": "V_PRODUCTION_MONTHLY",
        "description": (
            "Monthly oil, gas, and water production per well. "
            "Use for production volumes, rates, and trends over time. "
            "Primary key is (UWI, PROD_DATE). Join to other views on UWI."
        ),
        "columns": [
            {"name": "UWI",           "type": "VARCHAR2", "description": "Well identifier."},
            {"name": "WELL_NAME",     "type": "VARCHAR2", "description": "Well name."},
            {"name": "OPERATOR",      "type": "VARCHAR2", "description": "Operating company."},
            {"name": "FIELD_NAME",    "type": "VARCHAR2", "description": "Field name."},
            {"name": "PROD_DATE",     "type": "DATE",     "description": "First day of the production month."},
            {"name": "PROD_YEAR",     "type": "NUMBER",   "description": "Year extracted from PROD_DATE."},
            {"name": "PROD_MONTH",    "type": "NUMBER",   "description": "Month number (1-12) extracted from PROD_DATE."},
            {"name": "OIL_BBL",       "type": "NUMBER",   "description": "Oil produced in barrels that month."},
            {"name": "GAS_MCF",       "type": "NUMBER",   "description": "Gas produced in thousand cubic feet that month."},
            {"name": "WATER_BBL",     "type": "NUMBER",   "description": "Water produced in barrels that month."},
            {"name": "HOURS_ON",      "type": "NUMBER",   "description": "Hours the well was producing that month."},
            {"name": "OIL_RATE_BOPD", "type": "NUMBER",   "description": "Average oil rate in barrels per operating day."},
            {"name": "GAS_RATE_MCFPD","type": "NUMBER",   "description": "Average gas rate in MCF per operating day."},
        ],
        "join_keys": ["UWI"],
        "example_questions": [
            "Show monthly oil production for well ONGC-KG-001 in 2022.",
            "Which field produced the most oil in 2023?",
            "What is the total cumulative gas production for Reliance wells?",
        ]
    },
    {
        "view_name": "V_FORMATION_TOPS",
        "description": (
            "Stratigraphic formation tops per well. One row per (well, formation) pair. "
            "Use for depth, thickness, and lithology of geological formations. "
            "Join to other views on UWI."
        ),
        "columns": [
            {"name": "UWI",         "type": "VARCHAR2", "description": "Well identifier."},
            {"name": "WELL_NAME",   "type": "VARCHAR2", "description": "Well name."},
            {"name": "BASIN",       "type": "VARCHAR2", "description": "Sedimentary basin."},
            {"name": "FORMATION",   "type": "VARCHAR2", "description": "Geological formation name."},
            {"name": "TOP_DEPTH_M", "type": "NUMBER",   "description": "Depth to the top of the formation in metres."},
            {"name": "BASE_DEPTH_M","type": "NUMBER",   "description": "Depth to the base of the formation in metres."},
            {"name": "THICKNESS_M", "type": "NUMBER",   "description": "Formation thickness = BASE_DEPTH_M - TOP_DEPTH_M."},
            {"name": "LITHOLOGY",   "type": "VARCHAR2", "description": "Rock type: SANDSTONE, LIMESTONE, SHALE, or DOLOMITE."},
        ],
        "join_keys": ["UWI"],
        "example_questions": [
            "How thick is the Rajahmundry formation across all wells?",
            "List all sandstone formations in the Cambay basin.",
        ]
    },
    {
        "view_name": "V_WELL_SUMMARY",
        "description": (
            "Aggregated lifetime statistics per well. One row per well. "
            "Use for dashboard-level questions about cumulative production, average reservoir quality, "
            "and well performance comparisons. Do not use for time-series or depth-series queries. "
            "Join on UWI."
        ),
        "columns": [
            {"name": "UWI",                  "type": "VARCHAR2"},
            {"name": "WELL_NAME",            "type": "VARCHAR2"},
            {"name": "OPERATOR",             "type": "VARCHAR2"},
            {"name": "FIELD_NAME",           "type": "VARCHAR2"},
            {"name": "WELL_TYPE",            "type": "VARCHAR2"},
            {"name": "WELL_STATUS",          "type": "VARCHAR2"},
            {"name": "SPUD_DATE",            "type": "DATE"},
            {"name": "TOTAL_DEPTH_M",        "type": "NUMBER"},
            {"name": "CUMULATIVE_OIL_BBL",   "type": "NUMBER",   "description": "Total oil produced over the well's life in barrels."},
            {"name": "CUMULATIVE_GAS_MCF",   "type": "NUMBER",   "description": "Total gas produced over the well's life in MCF."},
            {"name": "CUMULATIVE_WATER_BBL", "type": "NUMBER",   "description": "Total water produced over the well's life in barrels."},
            {"name": "PRODUCING_MONTHS",     "type": "NUMBER",   "description": "Number of months the well has produced."},
            {"name": "AVG_POROSITY",         "type": "NUMBER",   "description": "Average porosity across all petrophysics samples for this well."},
            {"name": "AVG_PERMEABILITY",     "type": "NUMBER",   "description": "Average permeability in mD."},
        ],
        "join_keys": ["UWI"],
    },
    {
        "view_name": "V_CORE_ANALYSIS",
        "description": (
            "Laboratory core analysis results. One row per core run per well. "
            "Use for grain density, bulk density, recovery percentage, and computed porosity from core. "
            "Join on UWI."
        ),
        "columns": [
            {"name": "UWI",              "type": "VARCHAR2"},
            {"name": "WELL_NAME",        "type": "VARCHAR2"},
            {"name": "FIELD_NAME",       "type": "VARCHAR2"},
            {"name": "CORE_RUN",         "type": "NUMBER",   "description": "Sequential core run number for the well."},
            {"name": "TOP_DEPTH_M",      "type": "NUMBER"},
            {"name": "BASE_DEPTH_M",     "type": "NUMBER"},
            {"name": "GRAIN_DENSITY",    "type": "NUMBER",   "description": "Grain density in g/cc."},
            {"name": "BULK_DENSITY",     "type": "NUMBER",   "description": "Bulk density in g/cc."},
            {"name": "RECOVERY_PCT",     "type": "NUMBER",   "description": "Core recovery percentage (0-100)."},
            {"name": "COMPUTED_POROSITY","type": "NUMBER",   "description": "Porosity computed from density: 1 - bulk/grain."},
        ],
        "join_keys": ["UWI"],
    },
]

UWI_UBHI_RULE = (
    "CRITICAL JOIN RULE: UWI (Unique Well Identifier) and UBHI (Unique Borehole Identifier) "
    "refer to the same physical wellbore in this dataset. You can always join across views using "
    "UWI = UWI, UBHI = UBHI, or UWI = UBHI interchangeably. "
    "V_WELL_HEADER exposes both UWI and UBHI columns (UBHI is an alias of UWI). "
    "V_PETROPHYSICS is keyed on UBHI but also exposes UWI."
)

ORACLE_SYNTAX_RULES = (
    "ORACLE SQL RULES: "
    "Use FETCH FIRST n ROWS ONLY instead of LIMIT. "
    "Use NVL() instead of COALESCE() where possible. "
    "Use TO_DATE('2020-01-01','YYYY-MM-DD') for date literals. "
    "Use EXTRACT(YEAR FROM date_col) for year. "
    "Use TRUNC(date_col, 'MM') for month truncation. "
    "Use ROWNUM only in subqueries. "
    "Do not use backtick quoting. Use double-quotes for identifiers only when necessary. "
    "All view names are prefixed with the schema: welldata.V_VIEW_NAME. "
    "Always qualify column names with the view alias when joining multiple views."
)
