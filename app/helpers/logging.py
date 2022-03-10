def dict_to_log_string(dict_data):
    return ', '.join([f"{k}: '{v}'" for k, v in dict_data.items()])
