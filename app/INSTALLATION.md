# Installation Guide

## The Dependency Issue

This project has dependencies installed from git repositories:
- `aioesphomeserver` (from GitHub)
- `apigpio-mpf` (from GitHub)

These are **not available on PyPI**, which means the built wheel cannot be installed with standard `pip install` alone.

## Installation Methods

### Method 1: Using uv (Recommended for Development & Production)

```bash
cd /home/pi/chicken

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install the project with all dependencies
uv sync

# Verify installation
uv run chicken-door2 --help
```

**Advantages:**
- ✅ Handles git dependencies automatically
- ✅ Fast dependency resolution
- ✅ Lock file for reproducible installs
- ✅ Native support for [tool.uv.sources]

### Method 2: Using pip (Manual Git Dependencies)

If you must use pip, install git dependencies first:

```bash
cd /home/pi/chicken
source .venv/bin/activate

# Install git dependencies manually
pip install git+https://github.com/peterkeen/aioesphomeserver.git
pip install git+https://github.com/2e0byo/apigpio.git

# Then install other dependencies
pip install colored>=2.2.4 pyserial-asyncio>=0.6

# Finally install the application from source
pip install -e .

# Or from wheel (after git deps installed):
pip install ./dist/chicken_coop_app-0.1.1-py3-none-any.whl
```

**Disadvantages:**
- ❌ Manual dependency management
- ❌ Two-step installation process
- ❌ No automatic git dependency resolution

### Method 3: Direct Source Installation (Development Only)

```bash
cd /home/pi/chicken
source .venv/bin/activate

# Install in editable mode
pip install -e .
```

This won't work if git dependencies aren't pre-installed.

## Production Deployment

**For systemd service on Raspberry Pi, use Method 1 (uv):**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
cd /home/pi
git clone <repository-url> chicken
cd chicken

# Setup environment
uv venv
source .venv/bin/activate

# Install all dependencies
uv sync

# Verify
.venv/bin/chicken-door2 --help
```

Update systemd service to use the uv-created virtualenv:

```ini
ExecStart = /home/pi/chicken/.venv/bin/chicken-door2 --log-level INFO
```

## Building Distribution Wheels

### For Development/Testing

```bash
# Build with uv
make dist

# Output: dist/chicken_coop_app-0.1.1-py3-none-any.whl
```

**Note:** This wheel can only be installed if git dependencies are pre-installed (see Method 2).

### For PyPI-Compatible Distribution

To create a truly standalone wheel, you would need to:
1. Fork the git dependencies and publish them to PyPI, OR
2. Vendor the dependencies into your project, OR
3. Use only PyPI-available packages

**Current approach:** Use `uv` for installation which handles git dependencies transparently.

## Troubleshooting

### "Could not find a version that satisfies the requirement aioesphomeserver"

**Cause:** Trying to `pip install` the wheel without git dependencies pre-installed.

**Solution:** Use Method 1 (uv) or Method 2 (manual git install first).

### "ModuleNotFoundError: No module named 'aioesphomeserver'"

**Cause:** Dependencies not installed.

**Solution:**
```bash
# With uv:
uv sync

# With pip:
pip install git+https://github.com/peterkeen/aioesphomeserver.git
pip install git+https://github.com/2e0byo/apigpio.git
```

### Updating Dependencies

```bash
# With uv (recommended):
cd /home/pi/chicken
source .venv/bin/activate
uv sync

# With pip:
pip install --upgrade git+https://github.com/peterkeen/aioesphomeserver.git
pip install --upgrade git+https://github.com/2e0byo/apigpio.git
```

## Makefile Commands

All Makefile commands use `uv`:

```bash
make install    # uv sync
make run        # uv run chicken-door2
make build      # uv sync (prepare for deployment)
make dist       # uv build (create wheel)
```

## Why uv?

- **Modern Python packaging tool** by Astral (creators of Ruff)
- **Native git dependency support** via [tool.uv.sources]
- **Fast dependency resolution** (Rust-based)
- **Lock files** for reproducible environments
- **Drop-in pip replacement** with better UX

## Summary

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **uv sync** | Production & Dev | ✅ Simple<br>✅ Fast<br>✅ Git deps | Requires uv |
| **pip + manual git** | Legacy systems | ✅ Standard pip | ❌ Manual steps<br>❌ Complex |
| **pip install wheel** | ❌ Not supported | - | ❌ Missing git deps |

**Recommendation:** Use `uv` for all installations (dev and production).
