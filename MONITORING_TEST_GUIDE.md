# Monitoring Test Guide - Expense Tracker

This guide walks you through testing the complete monitoring stack (Health Endpoint, Prometheus Metrics, and Grafana Dashboard).

## Prerequisites

- Docker and Docker Compose installed
- All code changes from Branch 6 (monitoring-health) are complete

## Step-by-Step Testing Guide

### Step 1: Start All Services

Navigate to the project directory and start all services:

```bash
cd /Users/borja/Desktop/Expense_Tracker
docker-compose -f docker-compose.monitoring.yml up --build
```

**Expected Output:**
- All three services (app, prometheus, grafana) should start
- You should see logs from all services
- Wait until you see "Application is ready" messages

**What to check:**
- ✅ No error messages in the logs
- ✅ All services report as "healthy" after startup

---

### Step 2: Verify Application is Running

Open a new terminal (keep Docker Compose running) and test the application:

```bash
# Test health endpoint
curl http://localhost:5001/api/health

# Test metrics endpoint
curl http://localhost:5001/metrics
```

**Expected Output:**

**Health endpoint response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 123.45,
  "uptime": "2m 3s",
  "database": {
    "connected": true,
    "error": null
  },
  "timestamp": "2025-11-26T..."
}
```

**Metrics endpoint response:**
- Should return Prometheus-formatted metrics
- Should include `http_requests_total`, `http_request_duration_seconds`, etc.

**What to check:**
- ✅ Health endpoint returns `"status": "healthy"`
- ✅ Database shows `"connected": true`
- ✅ Metrics endpoint returns text with metric names

---

### Step 3: Generate Some Traffic

Make some requests to generate metrics:

```bash
# Make some HTTP requests
curl http://localhost:5001/
curl http://localhost:5001/api/health
curl http://localhost:5001/metrics

# Test signup (creates a user and generates metrics)
curl -X POST http://localhost:5001/api/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Test signin
curl -X POST http://localhost:5001/api/signin \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

**What to check:**
- ✅ All requests return appropriate HTTP status codes
- ✅ Metrics are being collected (check `/metrics` endpoint again)

---

### Step 4: Verify Prometheus is Scraping Metrics

Open your browser and navigate to:
```
http://localhost:9090
```

**In Prometheus UI:**

1. **Check Targets:**
   - Go to: Status → Targets
   - You should see `expense-tracker` job
   - Status should be **UP** (green)

2. **Query Metrics:**
   - Go to the Graph tab
   - Try these queries:
     ```
     rate(http_requests_total{job="expense-tracker"}[5m])
     rate(http_errors_total{job="expense-tracker"}[5m])
     histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="expense-tracker"}[5m]))
     ```

**What to check:**
- ✅ Target status is UP
- ✅ Queries return data (not "No data")
- ✅ Metrics show recent values

---

### Step 5: Access Grafana and Configure Data Source

Open your browser and navigate to:
```
http://localhost:3000
```

**Login:**
- Username: `admin`
- Password: `admin` (you'll be prompted to change it)

**Verify Prometheus Data Source:**
- Go to: Configuration → Data Sources
- You should see **Prometheus** already configured (auto-provisioned)
- Click on it and click "Save & Test"
- Should show: "Data source is working"

**If Prometheus is NOT auto-configured:**
1. Click "Add data source"
2. Select "Prometheus"
3. URL: `http://prometheus:9090`
4. Click "Save & Test"

**What to check:**
- ✅ Prometheus data source is configured
- ✅ "Data source is working" message appears

---

### Step 6: Import Dashboard

**If dashboard is auto-imported:**
- Go to: Dashboards → Browse
- You should see "Expense Tracker - Monitoring Dashboard"
- Click on it to open

**If dashboard is NOT auto-imported:**
1. Go to: Dashboards → Import
2. Click "Upload JSON file"
3. Navigate to: `grafana/dashboards/expense-tracker.json`
4. Select Prometheus as data source
5. Click "Import"

**What to check:**
- ✅ Dashboard loads without errors
- ✅ All panels are visible
- ✅ Panels show "No data" initially (normal - metrics will appear as traffic increases)

---

### Step 7: Generate Traffic and Watch Metrics

Keep the dashboard open and generate more traffic:

```bash
# In your terminal, run this loop to generate requests:
for i in {1..20}; do
  curl -s http://localhost:5001/api/health > /dev/null
  curl -s http://localhost:5001/ > /dev/null
  sleep 1
done
```

**Watch the Grafana Dashboard:**
- Panels should update in real-time (refresh every 10 seconds)
- You should see:
  - Request Rate panel showing requests per second
  - Error Rate panel showing any errors
  - Response Time panel showing latency percentiles

**What to check:**
- ✅ Metrics appear in dashboard panels
- ✅ Values update as you generate traffic
- ✅ Request rate increases
- ✅ Response times are displayed

---

### Step 8: Test Error Tracking

Generate some errors to see error tracking:

```bash
# Request non-existent endpoint (404)
curl http://localhost:5001/nonexistent

# Request without authentication (401)
curl http://localhost:5001/api/expenses

# Invalid request (400)
curl -X POST http://localhost:5001/api/signup \
  -H "Content-Type: application/json" \
  -d '{"invalid":"data"}'
```

**Check Grafana Dashboard:**
- Error Rate panel should show errors
- Error count should increase

**Check Prometheus:**
- Query: `rate(http_errors_total{job="expense-tracker"}[5m])`
- Should show error rate > 0

**What to check:**
- ✅ Errors are tracked in metrics
- ✅ Error rate panel shows errors
- ✅ Error count increases

---

### Step 9: Test Health Endpoint Status Changes

Test the health endpoint with different scenarios:

```bash
# Current health status
curl http://localhost:5001/api/health | jq .

# The status should be "healthy" when database is connected
```

**What to check:**
- ✅ Status shows "healthy"
- ✅ Database connectivity is true
- ✅ Uptime information is displayed

---

### Step 10: Verify All Components

**Final Verification Checklist:**

✅ **Application** (`http://localhost:5001`)
- Health endpoint works: `/api/health`
- Metrics endpoint works: `/metrics`
- Application functions normally

✅ **Prometheus** (`http://localhost:9090`)
- Target is UP (Status → Targets)
- Can query metrics (Graph tab)
- Metrics are being scraped every 15 seconds

✅ **Grafana** (`http://localhost:3000`)
- Prometheus data source is configured
- Dashboard is imported and visible
- Metrics are displaying in panels
- Dashboard refreshes automatically (10s)

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker logs
docker-compose -f docker-compose.monitoring.yml logs

# Check specific service
docker-compose -f docker-compose.monitoring.yml logs app
docker-compose -f docker-compose.monitoring.yml logs prometheus
docker-compose -f docker-compose.monitoring.yml logs grafana
```

### Prometheus Can't Scrape Metrics

1. Check if app is running: `curl http://localhost:5001/metrics`
2. Check Prometheus targets: `http://localhost:9090/targets`
3. Check Prometheus logs: `docker-compose -f docker-compose.monitoring.yml logs prometheus`

### Grafana Shows "No Data"

1. Verify Prometheus data source is working
2. Check if Prometheus has data: `http://localhost:9090/graph`
3. Generate more traffic to create metrics
4. Wait a few minutes for metrics to accumulate

### Port Already in Use

```bash
# Check what's using the ports
lsof -i :5001  # Application
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana

# Stop services
docker-compose -f docker-compose.monitoring.yml down
```

---

## Cleanup

To stop all services:

```bash
docker-compose -f docker-compose.monitoring.yml down
```

To stop and remove all data (volumes):

```bash
docker-compose -f docker-compose.monitoring.yml down -v
```

---

## Success Criteria

All of the following should work:

1. ✅ Application runs and responds to requests
2. ✅ Health endpoint shows healthy status
3. ✅ Metrics endpoint exposes Prometheus metrics
4. ✅ Prometheus scrapes metrics successfully
5. ✅ Grafana connects to Prometheus
6. ✅ Dashboard displays metrics correctly
7. ✅ Metrics update in real-time as traffic is generated

---

**Congratulations!** 🎉 

Your monitoring stack is now fully operational! You can use this setup to monitor your application's health, performance, and errors in real-time.

