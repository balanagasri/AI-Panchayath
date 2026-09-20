import logging
import os
from collections.abc import Iterable
from datetime import datetime
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.models.complaint import Complaint
from app.models.issue import IssueDetails

logger = logging.getLogger('civicsignal')


class DynamoDBUnavailableError(RuntimeError):
    """Raised when CivicSignal cannot reach or initialize DynamoDB."""


class InMemoryStore:
    backend_name = 'local'

    def __init__(self) -> None:
        self._complaints: list[Complaint] = []
        self._issues: list[IssueDetails] = []

    def save_complaint(self, complaint: Complaint) -> None:
        self._complaints.append(complaint)

    def list_complaints(self) -> list[Complaint]:
        return list(self._complaints)

    def replace_issues(self, issues: Iterable[IssueDetails]) -> None:
        self._issues = list(issues)

    def list_issues(self) -> list[IssueDetails]:
        return list(self._issues)

    def get_issue(self, issue_id: str) -> IssueDetails | None:
        for issue in self._issues:
            if issue.id == issue_id:
                return issue
        return None


class DynamoDBStore:
    backend_name = 'dynamodb'

    def __init__(self) -> None:
        self.region = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
        self.table_name = os.getenv('CIVICSIGNAL_TABLE_NAME', 'CivicSignal')
        self.endpoint_url = os.getenv('CIVICSIGNAL_DYNAMODB_ENDPOINT_URL')
        self._table = None

    def _get_table(self):
        if self._table is not None:
            return self._table
        if not self.region:
            raise DynamoDBUnavailableError('AWS_REGION must be set before using DynamoDB.')
        try:
            dynamodb = boto3.resource('dynamodb', region_name=self.region, endpoint_url=self.endpoint_url)
            table = dynamodb.Table(self.table_name)
            try:
                table.load()
            except ClientError as error:
                if error.response.get('Error', {}).get('Code') != 'ResourceNotFoundException':
                    raise
                table = dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[{'AttributeName': 'pk', 'KeyType': 'HASH'}, {'AttributeName': 'sk', 'KeyType': 'RANGE'}],
                    AttributeDefinitions=[{'AttributeName': 'pk', 'AttributeType': 'S'}, {'AttributeName': 'sk', 'AttributeType': 'S'}],
                    BillingMode='PAY_PER_REQUEST',
                )
                table.wait_until_exists()
            self._table = table
            return table
        except (BotoCoreError, ClientError, NoCredentialsError) as error:
            raise DynamoDBUnavailableError(
                f'Unable to use DynamoDB table {self.table_name!r} in region {self.region!r}. '
                'Check AWS credentials, region, permissions, and network connectivity.'
            ) from error

    def save_complaint(self, complaint: Complaint) -> None:
        table = self._get_table()
        table.put_item(Item={
            'pk': 'COMPLAINTS',
            'sk': self._complaint_key(complaint),
            'entity_type': 'complaint',
            'id': complaint.id,
            'description': complaint.description,
            'location': complaint.location,
            'category': complaint.category,
            'image_reference': complaint.image_reference,
            'created_at': complaint.created_at.isoformat(),
        })

    def list_complaints(self) -> list[Complaint]:
        response = self._get_table().query(
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={':pk': 'COMPLAINTS'},
            ScanIndexForward=False,
        )
        return [self._complaint_from_item(item) for item in response.get('Items', [])]

    def replace_issues(self, issues: Iterable[IssueDetails]) -> None:
        table = self._get_table()
        existing = table.query(
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={':pk': 'ISSUES'},
            ProjectionExpression='pk, sk',
        ).get('Items', [])
        with table.batch_writer() as batch:
            for item in existing:
                batch.delete_item(Key={'pk': item['pk'], 'sk': item['sk']})
            for issue in issues:
                batch.put_item(Item={
                    'pk': 'ISSUES',
                    'sk': issue.id,
                    'entity_type': 'issue',
                    **issue.model_dump(),
                })

    def list_issues(self) -> list[IssueDetails]:
        response = self._get_table().query(
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={':pk': 'ISSUES'},
            ScanIndexForward=True,
        )
        return [IssueDetails.model_validate(item) for item in response.get('Items', [])]

    def get_issue(self, issue_id: str) -> IssueDetails | None:
        response = self._get_table().get_item(Key={'pk': 'ISSUES', 'sk': issue_id})
        item = response.get('Item')
        return IssueDetails.model_validate(item) if item else None

    @staticmethod
    def _complaint_key(complaint: Complaint) -> str:
        return f'COMPLAINT#{complaint.created_at.isoformat()}#{complaint.id}'

    @staticmethod
    def _complaint_from_item(item: dict[str, Any]) -> Complaint:
        return Complaint(
            id=item['id'],
            description=item['description'],
            location=item['location'],
            category=item['category'],
            image_reference=item.get('image_reference'),
            created_at=datetime.fromisoformat(item['created_at']),
        )


_local_store = InMemoryStore()


class CivicSignalStore:
    def __init__(self) -> None:
        self._backend = None
        self._config_key = None

    @property
    def backend_name(self) -> str:
        return self._resolve_backend().backend_name

    def _resolve_backend(self):
        region = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
        credentials_available = any(
            os.getenv(var) for var in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_PROFILE', 'AWS_SESSION_TOKEN')
        )
        config_key = (
            region,
            credentials_available,
            os.getenv('CIVICSIGNAL_DYNAMODB_ENDPOINT_URL'),
            os.getenv('CIVICSIGNAL_TABLE_NAME', 'CivicSignal'),
        )
        if self._backend is not None and self._config_key == config_key:
            return self._backend

        if region and credentials_available:
            try:
                backend = DynamoDBStore()
                backend._get_table()
                self._backend = backend
                self._config_key = config_key
                logger.info('CivicSignal is using DynamoDB storage.')
                return backend
            except DynamoDBUnavailableError as exc:
                logger.warning('DynamoDB unavailable; falling back to local in-memory storage. %s', exc)

        self._backend = _local_store
        self._config_key = config_key
        logger.info('CivicSignal is using local in-memory storage because AWS_REGION or AWS credentials are unavailable.')
        return self._backend

    def save_complaint(self, complaint: Complaint) -> None:
        self._resolve_backend().save_complaint(complaint)

    def list_complaints(self) -> list[Complaint]:
        return self._resolve_backend().list_complaints()

    def replace_issues(self, issues: Iterable[IssueDetails]) -> None:
        self._resolve_backend().replace_issues(issues)

    def list_issues(self) -> list[IssueDetails]:
        return self._resolve_backend().list_issues()

    def get_issue(self, issue_id: str) -> IssueDetails | None:
        return self._resolve_backend().get_issue(issue_id)


dynamodb_store = CivicSignalStore()