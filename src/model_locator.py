import os
import dotenv


def __load_model_env(model: str) -> str:
    path_from_env_file = os.getenv(model, '')
    file_exist = os.path.isfile(path_from_env_file)
    if file_exist:
        return path_from_env_file

    path_inside_container = os.getenv(model + '_DEV', '')
    file_exist = os.path.isfile(path_inside_container)
    if file_exist:
        return path_inside_container

    raise NameError(f'Unable to locate model from env {model}')


dotenv.load_dotenv()
LABELING = __load_model_env('MODEL_LABELING')
CLASSIFICATION = __load_model_env('MODEL_CLASSIFICATION')
