import yaml
import os

try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False


class ConfigReader:
    def __init__(self):
        self.config = {}
        self.config_path = "config/config.yaml"

    def load(self):
        # Load .env first so env vars override config.yaml
        if _DOTENV_AVAILABLE:
            load_dotenv(override=False)  # don't override vars already in environment

        if not os.path.exists(self.config_path):
            raise FileNotFoundError("config.yaml not found")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Apply env var overrides — keeps secrets out of config.yaml
        self._apply_env_overrides()

        print("config loaded")

    def _apply_env_overrides(self):
        """Override config values from environment variables."""
        overrides = {
            "HF_TOKEN":    ("huggingface", "token"),
            "HF_REPO":     ("huggingface", "repo"),
            "DB_PASSWORD": ("database", "password"),
            "DB_HOST":     ("database", "host"),
            "DB_NAME":     ("database", "name"),
            "DB_USER":     ("database", "user"),
            "SECRET_KEY":  ("auth", "secret_key"),
        }
        for env_var, (section, key) in overrides.items():
            value = os.getenv(env_var)
            if value:
                self.config.setdefault(section, {})[key] = value

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_modules(self) -> dict:
        return self.config.get("modules", {})

    def is_module_enabled(self, module_name: str) -> bool:
        return self.get_modules().get(module_name, False)