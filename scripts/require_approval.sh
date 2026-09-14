#!/bin/sh
# Fails unless the merge request carries at least REQUIRED_APPROVALS approvals
# from someone other than its author.
set -eu

REQUIRED="${REQUIRED_APPROVALS:-1}"

if [ -z "${GITLAB_API_TOKEN:-}" ]; then
  echo "GITLAB_API_TOKEN is not set."
  echo "Create a project access token with the 'api' scope, then add it under"
  echo "Settings > CI/CD > Variables as GITLAB_API_TOKEN (masked)."
  exit 1
fi

# GET a path under this merge request. Prints the body; exits non-zero on any
# status other than 200 so a token or permissions problem fails loudly rather
# than silently reading as "no approvals".
api() {
  response=$(curl -s -w '\n%{http_code}' \
    --header "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
    "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID$1")
  status=$(printf '%s' "$response" | tail -n1)
  body=$(printf '%s' "$response" | sed '$d')
  if [ "$status" != "200" ]; then
    echo "GitLab API GET merge_requests/$CI_MERGE_REQUEST_IID$1 returned HTTP $status" >&2
    echo "$body" >&2
    return 1
  fi
  printf '%s' "$body"
}

# Kept out of a pipeline so a failing api() call aborts the script.
mr_json=$(api "")
author=$(printf '%s' "$mr_json" | jq -r '.author.username')

approvals_json=$(api "/approvals")
approvers=$(printf '%s' "$approvals_json" | jq -r --arg author "$author" \
  '[.approved_by[]?.user.username] | unique | map(select(. != $author)) | .[]')

count=$(printf '%s' "$approvers" | grep -c . || true)

echo ""
echo "Merge request !$CI_MERGE_REQUEST_IID by @$author"
if [ "$count" -gt 0 ]; then
  echo "Approved by:"
  printf '%s\n' "$approvers" | sed 's/^/  @/'
else
  echo "Approved by: nobody other than the author"
fi
echo ""

if [ "$count" -lt "$REQUIRED" ]; then
  echo "FAILED: $count of $REQUIRED required approval(s) from someone other than the author."
  echo "Approving does not re-run the pipeline, so re-run this job once the approval lands."
  exit 1
fi

echo "PASSED: $count approval(s) from someone other than the author, $REQUIRED required."
