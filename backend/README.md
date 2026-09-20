# CivicSignal backend

FastAPI backend for CivicSignal. Complaints and derived issues are persisted in one DynamoDB table named `CivicSignal`. Issue aggregation uses the existing local scikit-learn TF-IDF and cosine-similarity engine with civic issue profiles plus clustering for unseen patterns.

## Windows setup

From the project root:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The requirements include `scikit-learn`; reinstall with `pip install -r requirements.txt` after pulling backend changes.

## AWS and DynamoDB setup

The backend reads AWS configuration from environment variables and uses boto3's standard credential chain. It never contains AWS credentials. Create an IAM user or role with these DynamoDB permissions for the `CivicSignal` table:

- `dynamodb:DescribeTable`
- `dynamodb:CreateTable`
- `dynamodb:PutItem`
- `dynamodb:Query`
- `dynamodb:GetItem`
- `dynamodb:BatchWriteItem`

From PowerShell, configure credentials using the AWS CLI (this stores credentials in your local AWS profile, not in this repository):

```powershell
aws configure
```

Set the required backend configuration in the same PowerShell session:

```powershell
$env:AWS_REGION = 'us-east-1'
$env:CIVICSIGNAL_TABLE_NAME = 'CivicSignal'
```

Then start the API:

```powershell
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On the first data request, CivicSignal automatically creates the table with partition key `pk` and sort key `sk` using on-demand billing, then waits for it to become available. The backend fails with a clear configuration/connectivity error if DynamoDB cannot be reached; it never falls back to in-memory storage.

Copy `.env.example` for reference only. The backend does not load `.env` files automatically, so export the variables in your shell or configure them through your deployment environment.

For local DynamoDB or LocalStack, set `CIVICSIGNAL_DYNAMODB_ENDPOINT_URL` to the local endpoint and keep AWS credentials/configuration appropriate for that emulator.

The API is available at `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`.

## AWS Integration

CivicSignal uses Boto3, the AWS SDK for Python, and Amazon DynamoDB as its production persistence backend. The application retains a local in-memory fallback for local development and build/test scenarios when AWS credentials or AWS region configuration are unavailable.

No AWS credentials are hard-coded in the repository. The local demo is not storing data in Amazon DynamoDB; it remains a local development fallback.

## Endpoints

- `POST /api/complaints`
- `GET /api/complaints`
- `GET /api/issues`
- `GET /api/issues/{issue_id}`
- `GET /api/dashboard`
- `GET /api/aws-status`
- `GET /health`

## Single-table layout

- Complaint item: `pk=COMPLAINTS`, `sk=COMPLAINT#<created_at>#<id>`
- Derived issue item: `pk=ISSUES`, `sk=<issue_id>`
