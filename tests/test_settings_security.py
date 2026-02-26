import os
import subprocess
import sys
import pytest
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

def _run_settings_check(env_overrides, python_code='import django; import os; os.environ["DJANGO_SETTINGS_MODULE"]="config.settings"; django.setup(); print("OK")'):
    """Run a subprocess that imports Django settings with the given env vars.
    
    Returns (returncode, stdout, stderr).
    """
    env = {
        **os.environ,
        'DB_NAME': 'gym_db',
        'DB_USER': 'gym_user', 
        'DB_PASSWORD': '',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'PYTHONPATH': PROJECT_ROOT,
    }
    
    # Apply overrides (None means delete from env if present)
    for k, v in env_overrides.items():
        if v is None:
            if k in env:
                del env[k]
        else:
            env[k] = v
            
    # Also unset variables that might be injected by the system or .env that we want to control
    # But since we run in subprocess, the .env will be loaded BY config/settings.py!
    # IMPORTANT: load_dotenv(BASE_DIR / '.env') will NOT overwrite existing environment variables
    # by default (override=False is default). So passing them here overrides the .env file!
    
    executable = sys.executable

    result = subprocess.run(
        [executable, '-c', python_code],
        capture_output=True,
        text=True,
        env=env,
        cwd=PROJECT_ROOT,
        timeout=30,
    )
    return result.returncode, result.stdout.strip(), result.stderr

def _settings_load_succeeds(env_overrides):
    code, stdout, stderr = _run_settings_check(env_overrides)
    if code != 0:
        print(f"FAILED (code={code}): {stderr}")
    return code == 0 and 'OK' in stdout

def _settings_load_fails_with(env_overrides, expected_error_substr):
    code, stdout, stderr = _run_settings_check(env_overrides)
    return code != 0 and expected_error_substr in stderr

@pytest.mark.unit
def test_production_rejects_missing_secret_key():
    assert _settings_load_fails_with(
        {'ENVIRONMENT': 'production', 'SECRET_KEY': ''},
        'SECRET_KEY must be set to a strong unique value in production.'
    )

@pytest.mark.unit
def test_production_rejects_short_secret_key():
    assert _settings_load_fails_with(
        {'ENVIRONMENT': 'production', 'SECRET_KEY': 'short'},
        'SECRET_KEY must be set to a strong unique value in production.'
    )

@pytest.mark.unit
def test_production_rejects_insecure_secret_key():
    assert _settings_load_fails_with(
        {'ENVIRONMENT': 'production', 'SECRET_KEY': 'change-me'},
        'SECRET_KEY must be set to a strong unique value in production.'
    )

@pytest.mark.unit
def test_production_rejects_django_insecure_prefix():
    assert _settings_load_fails_with(
        {'ENVIRONMENT': 'production', 'SECRET_KEY': 'django-insecure-blahblahblahblahblahblahblah'},
        'SECRET_KEY must be set to a strong unique value in production.'
    )

@pytest.mark.unit
def test_production_rejects_debug_true():
    assert _settings_load_fails_with(
        {
            'ENVIRONMENT': 'production',
            'SECRET_KEY': 'valid-50-character-secret-key-that-is-very-long-and-secure',
            'DEBUG': 'True'
        },
        'DEBUG must be False in production.'
    )

@pytest.mark.unit
def test_production_with_valid_settings_succeeds():
    assert _settings_load_succeeds({
        'ENVIRONMENT': 'production',
        'SECRET_KEY': 'valid-50-character-secret-key-that-is-very-long-and-secure',
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'example.com'
    })

@pytest.mark.unit
def test_production_enables_secure_flags():
    python_code = (
        'import django; import os; os.environ["DJANGO_SETTINGS_MODULE"]="config.settings"; django.setup(); '
        'from django.conf import settings; '
        'print(f"{settings.SECURE_SSL_REDIRECT},{settings.SESSION_COOKIE_SECURE},{settings.CSRF_COOKIE_SECURE},{settings.SECURE_HSTS_SECONDS},{settings.SECURE_HSTS_INCLUDE_SUBDOMAINS},{settings.SECURE_HSTS_PRELOAD},{settings.SECURE_PROXY_SSL_HEADER}")'
    )
    code, stdout, stderr = _run_settings_check({
        'ENVIRONMENT': 'production',
        'SECRET_KEY': 'valid-50-character-secret-key-that-is-very-long-and-secure',
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'example.com'
    }, python_code=python_code)
    
    assert code == 0, f"Setup failed: {stderr}"
    assert stdout == 'True,True,True,31536000,True,True,(\'HTTP_X_FORWARDED_PROTO\', \'https\')'

@pytest.mark.unit
def test_non_production_defaults_are_developer_friendly():
    python_code = (
        'import django; import os; os.environ["DJANGO_SETTINGS_MODULE"]="config.settings"; django.setup(); '
        'from django.conf import settings; '
        'print(f"{settings.DEBUG},{settings.SECURE_SSL_REDIRECT},{settings.SESSION_COOKIE_SECURE},{settings.CSRF_COOKIE_SECURE},{settings.SECURE_HSTS_SECONDS}")'
    )
    # Without setting ENVIRONMENT, it should default to development
    code, stdout, stderr = _run_settings_check({
        'ENVIRONMENT': 'development',
        'SECRET_KEY': 'dev-only-insecure-secret-key',
        'DEBUG': 'False' # Override to False if .env says True
    }, python_code=python_code)
    
    assert code == 0, f"Setup failed: {stderr}"
    assert stdout == 'False,False,False,False,0'

@pytest.mark.unit
def test_non_production_allows_insecure_secret_key():
    # If we do not provide SECRET_KEY, it will fallback to insecure one, and because
    # ENVIRONMENT != 'production', it should not crash
    assert _settings_load_succeeds({
        'ENVIRONMENT': 'development',
        'SECRET_KEY': ''
    })

@pytest.mark.unit
def test_non_production_allows_debug_true():
    assert _settings_load_succeeds({
        'ENVIRONMENT': 'development',
        'DEBUG': 'True',
        'SECRET_KEY': ''
    })
