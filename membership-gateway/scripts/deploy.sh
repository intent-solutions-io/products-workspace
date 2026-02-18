#!/usr/bin/env bash
set -euo pipefail

# Intent Solutions Membership Gateway — Deploy to Cloud Run
#
# Prerequisites:
#   1. gcloud CLI authenticated with appropriate project
#   2. Secrets created in Secret Manager (see below)
#   3. Docker or Cloud Build enabled
#
# Usage:
#   GCP_PROJECT=your-project-id ./scripts/deploy.sh

PROJECT="${GCP_PROJECT:?Set GCP_PROJECT env var}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="membership-gateway"
DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Membership Gateway Deploy ==="
echo "Project: $PROJECT"
echo "Region:  $REGION"
echo "Service: $SERVICE"
echo ""

# 1. Ensure required secrets exist
echo "Checking secrets..."
SECRETS=(whop-webhook-secret github-token-members whop-api-key slack-webhook-url)
for secret in "${SECRETS[@]}"; do
  if ! gcloud secrets describe "$secret" --project="$PROJECT" &>/dev/null; then
    echo "  Creating secret: $secret"
    gcloud secrets create "$secret" \
      --project="$PROJECT" \
      --replication-policy=automatic
    echo "  WARNING: Secret '$secret' created but has no value. Add a version:"
    echo "    echo -n 'YOUR_VALUE' | gcloud secrets versions add $secret --data-file=- --project=$PROJECT"
  else
    echo "  OK: $secret"
  fi
done

# 2. Build and deploy
echo ""
echo "Building and deploying..."
gcloud run deploy "$SERVICE" \
  --source "$DIR" \
  --project="$PROJECT" \
  --region="$REGION" \
  --allow-unauthenticated \
  --set-secrets="WHOP_WEBHOOK_SECRET=whop-webhook-secret:latest,GITHUB_TOKEN=github-token-members:latest,WHOP_API_KEY=whop-api-key:latest,SLACK_WEBHOOK_URL=slack-webhook-url:latest" \
  --set-env-vars="GCP_PROJECT=$PROJECT" \
  --memory=256Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3 \
  --concurrency=80

# 3. Get the service URL
URL=$(gcloud run services describe "$SERVICE" \
  --project="$PROJECT" \
  --region="$REGION" \
  --format="value(status.url)")

echo ""
echo "=== Deploy Complete ==="
echo "Service URL: $URL"
echo "Health:      $URL/health"
echo "Webhook:     $URL/webhooks/whop"
echo "Sync:        $URL/sync"
echo ""
echo "Next steps:"
echo "  1. Add secret values if not already set:"
echo "     echo -n 'value' | gcloud secrets versions add SECRET_NAME --data-file=- --project=$PROJECT"
echo "  2. Register webhook in Whop:"
echo "     WHOP_API_KEY=... python scripts/register_webhook.py $URL"
echo "  3. Set up Cloud Scheduler for daily sync:"
echo "     gcloud scheduler jobs create http membership-sync \\"
echo "       --schedule='0 3 * * *' \\"
echo "       --uri='$URL/sync' \\"
echo "       --http-method=GET \\"
echo "       --project=$PROJECT \\"
echo "       --location=$REGION"
