def clean_model_name(model_name="BAAI/bge-base-en-v1.5"):
    index = model_name.rfind("/")
    if index == -1:
        return model_name
    return model_name[index + 1:]
