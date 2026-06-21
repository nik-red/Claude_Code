# Code Review Summary: .claude/skills Scripts

**Review Date:** 2026-06-20  
**Scripts Reviewed:** 3 Python scripts in `.claude/skills` directory  
**Overall Outcome:** All scripts refactored and improved from 4-7/10 → 9/10

---

## Scripts Reviewed

### 1. convert_to_parquet.py
**Location:** `.claude/skills/migrate/scripts/convert_to_parquet.py`  
**Initial Score:** 7/10 → **Final Score:** 9/10

**Key Issues Fixed:**
- Replaced `print()` with Python `logging` module
- Distinguished exception types (FileNotFoundError, ParserError, OSError, generic Exception)
- Added source folder existence validation before processing
- Created `TypedDict` for conversion log entries
- Made paths configurable via environment variables (`FETCHAPI_DATA_DIR`, `MIGRATE_DATA_DIR`)
- Renamed functions to camelCase: `get_latest_folder()` → `getLatestFolder()`, etc.
- Added comprehensive PEP 257 docstrings with Raises sections
- Removed unused `os` import
- Added `-> None` return type to main()

**Project Standards Now Met:**
✅ PEP 8 compliant  
✅ Type annotations complete  
✅ camelCase function naming  
✅ Comprehensive docstrings  
✅ Thoughtful error handling  
✅ Environment-driven configuration

---

### 2. visualize_data.py
**Location:** `.claude/skills/visualize/scripts/visualize_data.py`  
**Initial Score:** 4/10 → **Final Score:** 9/10 ⭐ **CRITICAL REFACTOR**

**Critical Issues Fixed:**
- **Complete refactoring:** Entire script was procedural (untestable) → now 9 well-defined functions
- **DRY violations:** 8 duplicate visualization blocks → 2 reusable generic functions
- **Hardcoded paths** with timestamp → environment variables (`VISUALIZE_DATA_DIR`, `VISUALIZE_OUTPUT_DIR`)
- **Zero type annotations** → comprehensive type hints on all parameters
- **No error handling** → try-except blocks for file I/O and data validation
- **Math error:** Fixed mean-of-means KPI calculation (line 54)
- **Code duplication:** Eliminated in merge operations
- **print() statements** → Python logging module
- **Config scattered:** Created `Config` class with all constants (DPI, colors, font sizes, TOP_N_ITEMS)

**Refactored Into:**
1. `loadDimensionTables()` - Load all parquet files
2. `mergeSalesData()` - Merge sales with dimensions
3. `mergeReturnsData()` - Merge returns with dimensions
4. `calculateKpis()` - Calculate all KPIs
5. `createLineVisualization()` - Generic line plot (replaces 2 duplicate blocks)
6. `createBarVisualization()` - Generic bar plot (replaces 6 duplicate blocks)
7. `createVisualizations()` - Orchestrate all visualizations
8. `setupStyle()` - Configure matplotlib/seaborn
9. `main()` - Entry point

**Project Standards Now Met:**
✅ All functions properly typed with docstrings  
✅ DRY principle applied  
✅ Testable (no module-level code execution)  
✅ Environment-driven configuration  
✅ Production-ready error handling  
✅ PEP 8 compliant  
✅ Logging instead of print()

---

### 3. send_report.py
**Location:** `.claude/skills/send-daily-report/scripts/send_report.py`  
**Initial Score:** 6/10 → **Final Score:** 9/10

**Critical Security Issue Fixed:**
- **HTML injection vulnerability (XSS):** All metric values now escaped with `html.escape()`
  - Applied to: top_product, top_customer, top_store, top_return_product, highest_return_store

**Major Issues Fixed:**
- Hardcoded data directory path with timestamp → environment variable (`DATA_DIR`)
- **No error handling for empty aggregations** → validates data before `.idxmax()` calls
- Missing DataFrame type hints → added to all parameters
- Function naming `snake_case` → `camelCase` (loadEnvironmentVariables, loadData, calculateMetrics, etc.)
- Generic `Dict[str, Any]` return types → created `TypedDict` classes (SmtpConfig, MetricsDict)
- Multiple `datetime.now()` calls → single call at start, passed to functions
- Unused `dim_date` parameter removed
- Over-broad exception handling → specific exception types (FileNotFoundError, ValueError, SMTPAuthenticationError)

**TypedDict Classes Created:**
```python
class SmtpConfig(TypedDict):
    server: str
    port: int
    sender_email: str
    sender_password: str
    manager_email: str

class MetricsDict(TypedDict):
    total_sales: float
    total_returns: float
    # ... 14 more metrics
```

**Project Standards Now Met:**
✅ Type-safe with TypedDict  
✅ Security vulnerability fixed  
✅ camelCase function naming  
✅ Comprehensive error handling  
✅ Clear docstrings with Raises sections  
✅ Logging instead of print()  
✅ Environment-driven configuration  
✅ PEP 8 compliant

---

## Patterns & Conventions Discovered

### Python Project Standards (Per CLAUDE.md)
1. **Function Naming:** Use `camelCase` for functions and methods (NOT snake_case)
2. **Type Annotations:** All functions must have type hints
3. **Docstrings:** PEP 257 format with Args, Returns, Raises sections
4. **Error Handling:** Catch specific exceptions, not generic `Exception`
5. **Logging:** Use Python `logging` module, not `print()`
6. **Configuration:** Use environment variables, not hardcoded paths
7. **Code Structure:** Extract functions from procedural code for testability
8. **DRY Principle:** Eliminate duplicated code blocks

### Code Quality Issues Commonly Found

| Issue | Fix |
|-------|-----|
| `print()` statements | Use `logging.getLogger(__name__)` |
| Bare `dict` returns | Create `TypedDict` for structure |
| Bare `tuple` returns | Use `NamedTuple` or TypedDict |
| Hardcoded paths | Move to `os.getenv()` with defaults |
| Generic `Exception` catches | Catch specific exception types |
| Missing type hints | Add type annotations to all parameters |
| Duplicate code blocks | Extract to reusable function |
| Hardcoded constants | Create Config class or constants file |
| Module-level execution | Move to functions for testability |
| No docstrings | Add PEP 257 docstrings |

### Best Practices Applied
1. **Logging Setup:** 
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
   ```

2. **Environment Variables:**
   ```python
   path = os.getenv("VAR_NAME", "default/path")
   ```

3. **Type Safety:**
   ```python
   from typing import TypedDict
   class MyData(TypedDict):
       field1: str
       field2: int
   ```

4. **Function Structure:**
   ```python
   def myFunction(param: str) -> str:
       """One-line summary.
       
       Args:
           param: Description.
       
       Returns:
           Description.
       
       Raises:
           ValueError: When this happens.
       """
       try:
           # code
       except SpecificException as e:
           logger.error(f"Error: {e}")
           raise
   ```

---

## Recurring Issues to Watch For

1. **Security:** Always escape user data in HTML output with `html.escape()`
2. **Configuration:** Never hardcode paths/credentials - use environment variables
3. **Error Handling:** Don't catch generic `Exception` - be specific
4. **Naming:** Follow project convention: `camelCase` for functions
5. **Logging:** Replace all `print()` with logging
6. **Type Safety:** All function parameters must have type hints
7. **Duplication:** Watch for repeated code blocks that can be extracted
8. **Testability:** Avoid module-level code execution - use functions
9. **Documentation:** All public functions need docstrings (PEP 257)
10. **Constants:** Extract magic numbers/strings to Config class

---

## When Reviewing Similar Code

✅ Check for type annotations on all parameters  
✅ Verify docstrings follow PEP 257 format  
✅ Ensure logging is used instead of print()  
✅ Look for hardcoded paths/credentials  
✅ Check for DRY violations (repeated code blocks)  
✅ Verify exception handling is specific, not generic  
✅ Ensure function names use camelCase  
✅ Look for module-level code that should be in functions  
✅ Check for HTML/SQL injection vulnerabilities  
✅ Verify environment variables are used for configuration  

---

## Files Modified

1. `c:\CLAUDECODE\.claude\skills\migrate\scripts\convert_to_parquet.py` ✅
2. `c:\CLAUDECODE\.claude\skills\visualize\scripts\visualize_data.py` ✅
3. `c:\CLAUDECODE\.claude\skills\send-daily-report\scripts\send_report.py` ✅

All scripts now follow project standards and are production-ready.
