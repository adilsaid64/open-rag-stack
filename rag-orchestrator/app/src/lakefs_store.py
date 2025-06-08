from lakefs.client import Client


class LakeFSLogger:
    """Commits documents to lakefs"""

    def __init__(
        self,
        lakefs_endpoint: str,
        lakefs_username: str,
        lakefs_password: str,
        lakefs_repo: str,
    ):
        self.lakefs_endpoint = lakefs_endpoint
        self.lakefs_username = lakefs_username
        self.lakefs_repo = lakefs_repo

        self.lakefs_client = Client(
            host=self.lakefs_endpoint,
            username=lakefs_username,
            password=lakefs_password,
        )
        self.lakfs_repo = ...

        self.lakefs_branch = ...

    def upload_document(self, document: str):
        """Uploads a document to lakefs and returns a commit hash"""
        ...
