import io
import uuid

import boto3
import lakefs
from boto3.resources.base import ServiceResource
from lakefs.client import Client


class LakeFSLogger:
    """Stores text passages in LakeFS and returns commit hashes"""

    def __init__(
        self,
        lakefs_endpoint: str,
        lakefs_username: str,
        lakefs_password: str,
        lakefs_repo: str,
        branch: str = "main",
    ):
        self.lakefs_endpoint = lakefs_endpoint
        self.lakefs_username = lakefs_username
        self.lakefs_repo = lakefs_repo
        self.branch = branch

        self.lakefs_client: Client = Client(
            host=self.lakefs_endpoint,
            username=self.lakefs_username,
            password=lakefs_password,
        )

        self.lakefs_resource: ServiceResource = boto3.resource(
            "s3",
            endpoint_url=self.lakefs_endpoint,
            aws_access_key_id=self.lakefs_username,
            aws_secret_access_key=lakefs_password,
        )

    def store_text(
        self,
        data: str,
    ):
        storage_key = f"{uuid.uuid4()}.json"
        data_vfile = io.BytesIO(data.encode("utf-8"))
        self.lakefs_repo.upload_fileobj(data_vfile, storage_key)
        branch = lakefs.Repository(self.lakefs_repo, client=self.lakefs_client).branch(
            self.branch
        )
        ref = branch.commit(message=f"pushing {storage_key} data to {self.branch}")
        return ref.get_commit()
