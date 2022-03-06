import os
import boto3

ssm_client = boto3.client("ssm")
env = os.environ.get("ENV", "dev")


def get_param(param):
    return ssm_client.get_parameter(Name=param)["Parameter"]["Value"]


def get_param_with_default(param, default=None):
    try:
        return ssm_client.get_parameter(Name=param)["Parameter"]["Value"]
    except Exception:
        if default:
            return default
        else:
            raise


class RelationalDB:
    @staticmethod
    def name(default=None):
        return get_param_with_default(f"/{env}/api/db_name", default)

    @staticmethod
    def port(default=None):
        return get_param_with_default(f"/{env}/api/db_port", default)

    @staticmethod
    def user(default=None):
        return get_param_with_default(f"/{env}/api/db_username", default)

    @staticmethod
    def host(default=None):
        return get_param_with_default(f"/{env}/api/db_host", default)

    @staticmethod
    def password(default=None):
        return get_param_with_default(f"/{env}/api/db_password", default)


# TODO: add to infra-aws repo
class S3Bucket:
    _media_bucket_label = "profile_pictures_bucket"

    def __init__(self):
        self.media_bucket = self._get_media_bucket()

    def _get_media_bucket(self):
        return get_param_with_default(f"/{env}/api/{self._media_bucket_label}")


# NOTE(john) - The purpose of these is to load the SSM params once on APP startup
# Otherwise each call to the parameter store is wasted time/latency
S3BucketConfig = S3Bucket()
RelationalDB = RelationalDB()
