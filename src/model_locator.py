import os
import dotenv


def __loadModelEnv(model: str) -> str:
    dotenv.load_dotenv()
    model_env_suffix = '_DEV' if ('DEV_CONTAINER' in os.environ) else ''
    model_env = model + model_env_suffix
    return os.environ[model_env]


def labeling() -> str:
    return __loadModelEnv('MODEL_LABELING')


def classification() -> str:
    return __loadModelEnv('MODEL_CLASSIFICATION')
