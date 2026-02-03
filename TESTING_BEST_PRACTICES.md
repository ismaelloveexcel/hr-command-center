# 🧪 Testing & Automation Best Practices

**Guide for addressing test coupling, dependency issues, and automation improvements**

---

## 📋 Overview

This document addresses:
1. Test coupling and dependency issues in automation scripts
2. Best practices for workflow independence
3. Edge case handling
4. Retry strategies

---

## 🔗 Test Coupling Issues

### Problem: Workflows with Hidden Dependencies

**Issue**: Workflows fail when run in isolation due to undocumented dependencies

**Example of Coupling**:
```yaml
# ❌ BAD: Assumes backend is already deployed
- name: Test API
  run: curl https://baynunah-hr-portal.azurewebsites.net/api
```

**Solution - Make Dependencies Explicit**:
```yaml
# ✅ GOOD: Check dependency exists first
- name: Verify backend is deployed
  run: |
    if ! az webapp show --name baynunah-hr-portal --resource-group baynunah-hr-portal-rg 2>/dev/null; then
      echo "❌ Backend not deployed. Run backend-bootstrap.yml first."
      exit 1
    fi

- name: Test API
  run: curl https://baynunah-hr-portal.azurewebsites.net/api
```

### Solution 1: Dependency Validation

Add validation steps to all workflows:

```yaml
jobs:
  validate-dependencies:
    runs-on: ubuntu-latest
    outputs:
      backend_ready: ${{ steps.check.outputs.backend }}
      frontend_ready: ${{ steps.check.outputs.frontend }}
    
    steps:
      - name: Check dependencies
        id: check
        run: |
          # Check backend
          if az webapp show --name $BACKEND_NAME --resource-group $RG 2>/dev/null; then
            echo "backend=true" >> $GITHUB_OUTPUT
          else
            echo "backend=false" >> $GITHUB_OUTPUT
          fi
          
          # Check frontend
          if az staticwebapp show --name $FRONTEND_NAME --resource-group $RG 2>/dev/null; then
            echo "frontend=true" >> $GITHUB_OUTPUT
          else
            echo "frontend=false" >> $GITHUB_OUTPUT
          fi
  
  deploy:
    needs: validate-dependencies
    if: needs.validate-dependencies.outputs.backend_ready == 'true'
    # ... rest of workflow
```

### Solution 2: Self-Contained Workflows

Make each workflow independently executable:

```yaml
# Each workflow should:
# 1. Validate prerequisites
# 2. Set up its own resources
# 3. Clean up after itself (if test)

jobs:
  setup:
    steps:
      - name: Ensure prerequisites
        run: |
          # Create resources if they don't exist
          if ! az group show --name $RG 2>/dev/null; then
            az group create --name $RG --location $LOCATION
          fi
```

---

## 🔄 Dependency Management

### Problem: Implicit Resource Dependencies

**Common Issues**:
1. Resource creation order matters
2. Propagation delays not handled
3. Transient failures not retried

### Solution: Explicit Dependency Graph

```yaml
jobs:
  # Job 1: Foundation
  create-resource-group:
    runs-on: ubuntu-latest
    steps:
      - name: Create RG
        run: az group create --name $RG --location $LOCATION
  
  # Job 2: Depends on Job 1
  create-infrastructure:
    needs: create-resource-group
    runs-on: ubuntu-latest
    steps:
      - name: Create App Service Plan
        uses: nick-fields/retry@v2
        with:
          max_attempts: 3
          retry_wait_seconds: 30
          command: az appservice plan create ...
  
  # Job 3: Depends on Job 2
  deploy-app:
    needs: create-infrastructure
    runs-on: ubuntu-latest
    steps:
      - name: Deploy application
        run: az webapp deployment ...
```

### Solution: Wait for Resource Ready State

```yaml
- name: Wait for resource to be ready
  run: |
    MAX_WAIT=300  # 5 minutes
    ELAPSED=0
    
    while [ $ELAPSED -lt $MAX_WAIT ]; do
      STATE=$(az webapp show --name $APP --resource-group $RG --query "state" -o tsv)
      
      if [ "$STATE" = "Running" ]; then
        echo "✅ App is ready"
        exit 0
      fi
      
      echo "Waiting for app to be ready (state: $STATE)..."
      sleep 10
      ELAPSED=$((ELAPSED + 10))
    done
    
    echo "❌ Timeout waiting for app to be ready"
    exit 1
```

---

## 🎯 Edge Case Handling

### Edge Case 1: Resource Name Conflicts

**Problem**: Resource names must be globally unique

**Solution**:
```yaml
- name: Ensure unique resource name
  id: naming
  run: |
    BASE_NAME="hrportal"
    SUFFIX=$(date +%s | tail -c 5)  # Last 4 digits of timestamp
    UNIQUE_NAME="${BASE_NAME}-${SUFFIX}"
    
    # Verify availability
    while az webapp list --query "[?name=='$UNIQUE_NAME'].name" -o tsv | grep -q .; do
      SUFFIX=$((SUFFIX + 1))
      UNIQUE_NAME="${BASE_NAME}-${SUFFIX}"
    done
    
    echo "name=$UNIQUE_NAME" >> $GITHUB_OUTPUT
    echo "✅ Using unique name: $UNIQUE_NAME"

- name: Create webapp
  run: |
    az webapp create --name ${{ steps.naming.outputs.name }} ...
```

### Edge Case 2: Quota Limits

**Problem**: Azure subscription quotas can be exceeded

**Solution**:
```yaml
- name: Check quota before creation
  run: |
    # Check current usage
    CURRENT=$(az vm list-usage --location $LOCATION \
                --query "[?localName=='Standard DSv3 Family vCPUs'].currentValue" -o tsv)
    LIMIT=$(az vm list-usage --location $LOCATION \
              --query "[?localName=='Standard DSv3 Family vCPUs'].limit" -o tsv)
    
    REQUIRED=2  # vCPUs needed
    AVAILABLE=$((LIMIT - CURRENT))
    
    if [ $AVAILABLE -lt $REQUIRED ]; then
      echo "❌ Insufficient quota: need $REQUIRED vCPUs, only $AVAILABLE available"
      echo "Request quota increase or use different SKU"
      exit 1
    fi
    
    echo "✅ Quota check passed: $AVAILABLE vCPUs available"
```

### Edge Case 3: Network Timeouts

**Problem**: Network issues cause intermittent failures

**Solution**:
```yaml
- name: Deploy with timeout handling
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 15
    max_attempts: 3
    retry_wait_seconds: 60
    on_retry_command: |
      echo "Deployment failed, checking status..."
      az webapp show --name $APP --resource-group $RG --query "state" -o tsv
    command: |
      az webapp deployment source config-zip \
        --resource-group $RG \
        --name $APP \
        --src deploy.zip \
        --timeout 600
```

### Edge Case 4: Partial Deployments

**Problem**: Deployment partially completes then fails

**Solution**:
```yaml
- name: Deploy with rollback on failure
  id: deploy
  run: |
    # Save current state
    CURRENT_TAG=$(az webapp deployment slot list \
                   --name $APP --resource-group $RG \
                   --query "[0].id" -o tsv)
    
    echo "current_tag=$CURRENT_TAG" >> $GITHUB_OUTPUT
    
    # Attempt deployment
    az webapp deployment source config-zip \
      --resource-group $RG \
      --name $APP \
      --src deploy.zip

- name: Verify deployment
  run: |
    # Check health
    if ! curl -sf https://$APP.azurewebsites.net/health; then
      echo "❌ Health check failed after deployment"
      exit 1
    fi

- name: Rollback on failure
  if: failure() && steps.deploy.outputs.current_tag != ''
  run: |
    echo "🔄 Rolling back to previous version..."
    az webapp deployment slot swap \
      --name $APP \
      --resource-group $RG \
      --slot production \
      --target-slot ${{ steps.deploy.outputs.current_tag }}
```

### Edge Case 5: Concurrent Modifications

**Problem**: Multiple workflows modifying same resources

**Solution**:
```yaml
concurrency:
  group: deployment-${{ github.ref }}
  cancel-in-progress: false  # Wait for previous deployment

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Acquire lock
        run: |
          LOCK_FILE="deployment.lock"
          MAX_WAIT=600  # 10 minutes
          
          while [ -f "$LOCK_FILE" ] && [ $SECONDS -lt $MAX_WAIT ]; do
            echo "Waiting for lock..."
            sleep 10
          done
          
          if [ -f "$LOCK_FILE" ]; then
            echo "❌ Timeout waiting for lock"
            exit 1
          fi
          
          echo $$ > $LOCK_FILE
          echo "✅ Lock acquired"
      
      - name: Deploy
        run: |
          # Deployment steps
          
      - name: Release lock
        if: always()
        run: rm -f deployment.lock
```

---

## 🔄 Retry Strategies

### Strategy 1: Exponential Backoff

```yaml
- name: Deploy with exponential backoff
  run: |
    MAX_ATTEMPTS=5
    ATTEMPT=1
    DELAY=10
    
    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
      echo "Attempt $ATTEMPT of $MAX_ATTEMPTS..."
      
      if az webapp deployment ...; then
        echo "✅ Success"
        exit 0
      fi
      
      if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        echo "Failed, waiting ${DELAY}s before retry..."
        sleep $DELAY
        DELAY=$((DELAY * 2))  # Double the delay
      fi
      
      ATTEMPT=$((ATTEMPT + 1))
    done
    
    echo "❌ All attempts failed"
    exit 1
```

### Strategy 2: Conditional Retry

```yaml
- name: Deploy with conditional retry
  run: |
    for i in {1..5}; do
      OUTPUT=$(az webapp deployment ... 2>&1)
      EXIT_CODE=$?
      
      if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Success"
        exit 0
      fi
      
      # Only retry on transient errors
      if echo "$OUTPUT" | grep -q "timeout\|network\|throttled"; then
        echo "Transient error, retrying..."
        sleep 30
      else
        echo "❌ Non-retryable error"
        echo "$OUTPUT"
        exit $EXIT_CODE
      fi
    done
```

### Strategy 3: Circuit Breaker

```yaml
- name: Deploy with circuit breaker
  run: |
    FAILURE_THRESHOLD=3
    FAILURE_COUNT=0
    CIRCUIT_OPEN=false
    
    for i in {1..10}; do
      if [ "$CIRCUIT_OPEN" = true ]; then
        echo "⚠️ Circuit breaker open, skipping attempts"
        sleep 60
        CIRCUIT_OPEN=false
        FAILURE_COUNT=0
        continue
      fi
      
      if az webapp deployment ...; then
        echo "✅ Success"
        FAILURE_COUNT=0
        exit 0
      else
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        
        if [ $FAILURE_COUNT -ge $FAILURE_THRESHOLD ]; then
          echo "⚠️ Opening circuit breaker"
          CIRCUIT_OPEN=true
        fi
      fi
      
      sleep 30
    done
```

---

## ✅ Implementation Checklist

### For Each Workflow

- [ ] Dependencies explicitly documented
- [ ] Prerequisites validated before execution
- [ ] Resources checked for existence
- [ ] Appropriate retry logic added
- [ ] Edge cases handled
- [ ] Timeout values set
- [ ] Error messages are actionable
- [ ] Cleanup on failure implemented
- [ ] Concurrency controls in place
- [ ] Integration tests passing

### For Each Resource Operation

- [ ] Check if resource exists first
- [ ] Handle "already exists" gracefully
- [ ] Use retry for transient failures
- [ ] Wait for ready state
- [ ] Verify operation success
- [ ] Log meaningful progress
- [ ] Provide rollback capability

---

## 📚 References

- [GitHub Actions Best Practices](https://docs.github.com/actions/learn-github-actions/essential-features-of-github-actions)
- [Azure Reliability Patterns](https://docs.microsoft.com/azure/architecture/patterns/category/reliability)
- [Retry Pattern](https://docs.microsoft.com/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://docs.microsoft.com/azure/architecture/patterns/circuit-breaker)

---

**Last Updated**: February 3, 2026  
**Status**: Production Ready  
**Maintained By**: DevOps Team
