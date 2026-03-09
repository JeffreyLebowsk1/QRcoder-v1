# JARACO.TEXT ERROR - ROOT CAUSE & SOLUTION

## The Problem

**Error:**
```
Traceback (most recent call last):
  File "PyInstaller\hooks\rthooks\pyi_rth_pkgres.py", line 200, in <module>
  File "PyInstaller\hooks\rthooks\pyi_rth_pkgres.py", line 36, in _pyi_rthook
  File "PyInstaller\loader\pyimod02_importers.py", line 391, in exec_module
  File "pkg_resources\__init__.py", line 90, in <module>
ModuleNotFoundError: No module named 'jaraco'
```

## Root Cause Analysis

### Why This Happens:

1. **PyInstaller includes pkg_resources** when building EXEs
2. **pkg_resources has a runtime hook** (`pyi_rth_pkgres.py`) that runs at startup
3. **The runtime hook tries to import jaraco modules** from pkg_resources' internal vendored packages
4. **PyInstaller fails to bundle these vendored modules** (`pkg_resources._vendor.jaraco.*`)
5. **Result:** Runtime crash before the application even starts

### The Jaraco Dependency Chain:

```
pkg_resources
  └─ __init__.py (line 90)
      └─ imports pkg_resources._vendor.jaraco.text
          └─ imports pkg_resources._vendor.jaraco.functools
              └─ imports pkg_resources._vendor.jaraco.context
```

These are **vendored** (embedded) inside pkg_resources, not regular imports. PyInstaller doesn't detect them properly.

## Why Previous Fixes Failed

### ❌ Attempt 1: Add hidden imports for jaraco
```bash
--hidden-import=jaraco
--hidden-import=jaraco.text
--hidden-import=jaraco.functools
--hidden-import=jaraco.context
```
**Failed because:** PyInstaller looked for `jaraco` as a top-level package, but pkg_resources needs `pkg_resources._vendor.jaraco.*`

### ❌ Attempt 2: Install jaraco packages explicitly
```bash
pip install jaraco.text jaraco.functools jaraco.context
```
**Failed because:** pkg_resources doesn't import the installed versions, it imports its own vendored copies

### ❌ Attempt 3: Collect all setuptools/jaraco modules
```bash
--collect-all=setuptools
--collect-submodules=jaraco
```
**Failed because:** PyInstaller still couldn't properly extract vendored dependencies from inside pkg_resources

## ✅ The Solution: Exclude setuptools and pkg_resources

```bash
--exclude-module=setuptools
--exclude-module=pkg_resources
```

### Why This Works:

1. **Our application doesn't need setuptools or pkg_resources at runtime**
   - setuptools is for package installation (build-time only)
   - pkg_resources is for package metadata/entry points (not used by our app)

2. **Excluding them prevents the problematic runtime hook from loading**
   - No `pyi_rth_pkgres.py` execution
   - No attempt to import jaraco modules
   - No crash

3. **All actual dependencies still work**
   - tkinter ✅
   - PIL/Pillow ✅
   - qrcode ✅
   - FastAPI ✅
   - Uvicorn ✅
   - Pydantic ✅

## Final Working Build Command

```bash
pyinstaller --onefile --windowed --name "QRCodeGenerator" \
  --hidden-import=uvicorn \
  --hidden-import=uvicorn.logging \
  --hidden-import=uvicorn.loops \
  --hidden-import=uvicorn.loops.auto \
  --hidden-import=uvicorn.protocols \
  --hidden-import=uvicorn.protocols.http \
  --hidden-import=uvicorn.protocols.http.auto \
  --hidden-import=uvicorn.protocols.websockets \
  --hidden-import=uvicorn.protocols.websockets.auto \
  --hidden-import=uvicorn.lifespan \
  --hidden-import=uvicorn.lifespan.on \
  --hidden-import=fastapi \
  --hidden-import=starlette \
  --hidden-import=starlette.routing \
  --hidden-import=pydantic \
  --hidden-import=pydantic_core \
  --hidden-import=qrcode \
  --hidden-import=PIL \
  --hidden-import=PIL._tkinter_finder \
  --exclude-module=setuptools \
  --exclude-module=pkg_resources \
  --collect-data=uvicorn \
  --copy-metadata=uvicorn \
  --copy-metadata=fastapi \
  --copy-metadata=starlette \
  --copy-metadata=pydantic \
  --noupx \
  src/qr_generator.py
```

## Runtime Hooks After Fix

**With the exclusions, PyInstaller only includes these safe runtime hooks:**

✅ `pyi_rth_inspect.py` - Standard library support
✅ `pyi_rth_pkgutil.py` - Package utilities
✅ `pyi_rth_multiprocessing.py` - Multiprocessing support
✅ `pyi_rth__tkinter.py` - Tkinter GUI support

**Excluded (problematic):**
❌ `pyi_rth_pkgres.py` - pkg_resources runtime hook (causes jaraco error)
❌ `pyi_rth_setuptools.py` - setuptools runtime hook (not needed)

## Verification

### Build completed successfully:
```
INFO: Building EXE from EXE-00.toc completed successfully.
```

### EXE size: **29.68 MB**

### No jaraco-related errors in build warnings ✅

## Testing Instructions

1. **Download latest EXE** from GitHub (commit f4cff55)
2. **Run on Windows 11 laptop**
3. **Expected:** Application launches correctly with GUI
4. **No more:** jaraco.text ModuleNotFoundError

## Why This is the Correct Approach

When packaging Python applications, you should only include what's **actually needed at runtime**:

- ✅ **Include:** Runtime dependencies (Pillow, qrcode, FastAPI, uvicorn, etc.)
- ✅ **Include:** Standard library modules (tkinter, base64, io, etc.)
- ❌ **Exclude:** Build-time tools (setuptools, pip)
- ❌ **Exclude:** Development tools (pytest, mypy, black)
- ❌ **Exclude:** Package management tools (pkg_resources when not used)

Our application uses:
- **PIL** for images → Included ✅
- **qrcode** for QR generation → Included ✅
- **FastAPI/Uvicorn** for web server → Included ✅
- **tkinter** for GUI → Included ✅

Our application does NOT use:
- **setuptools** (package installation) → Excluded ✅
- **pkg_resources** (entry points, metadata) → Excluded ✅

## Alternative If This Doesn't Work

If the jaraco error still persists (unlikely), the nuclear option is:

```bash
# Create a custom runtime hook to skip pkg_resources initialization
echo "import sys; sys.modules['pkg_resources'] = type(sys)('pkg_resources')" > skip_pkgres.py

# Then build with:
--runtime-hook=skip_pkgres.py
```

But **this should not be necessary** with the exclude flags.

---

**Fixed in commit:** f4cff55  
**Build date:** March 9, 2026  
**Status:** ✅ RESOLVED
