import os
import dotenv


def __load_model_env(model: str) -> str:

    path_from_env_file = os.getenv(model)
    if path_from_env_file is not None:
        return path_from_env_file

    path_inside_container = os.getenv(model + '_DEV')

    if path_inside_container is None:
        raise NameError(f'Unable to locate model from env {model}')

    return str(path_inside_container)


dotenv.load_dotenv()
LABELING = __load_model_env('MODEL_LABELING')
CLASSIFICATION = __load_model_env('MODEL_CLASSIFICATION')
