from pythonjsonlogger import jsonlogger


# NOTE(John) - Datadog requires us to use 'status' instead of 'levelname' for the severity
# https://docs.datadoghq.com/logs/log_configuration/attributes_naming_convention/#reserved-attributes
# https://stackoverflow.com/questions/52929290/how-can-i-rename-levelname-to-level-in-python-log-messages/52933068
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        # This changes what we have setup in the logger.ini config after the message is produced
        log_record['status'] = log_record['levelname']
        del log_record['levelname']
