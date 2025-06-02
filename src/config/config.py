import yaml
import os


def load_config_file(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def load_config():
    """
    Trả về cấu hình LLM từ file config.yaml.
    """
    # Get the absolute path to the settings directory
    settings_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(settings_dir, "config.yaml")
    config = load_config_file(yaml_path)
    if config is None:
        raise ValueError("❌ Không tìm thấy cấu hình trong file config.yaml.")

    # Load API key from environment variables
    config["llm_google"]["api_key"] = os.environ.get(
        "GOOGLE_API_KEY", config["llm_google"].get("api_key")
    )

    # Load Discord token from environment variables
    config["discord"]["token"] = os.environ.get(
        "DISCORD_TOKEN", config["discord"].get("token")
    )

    return config
