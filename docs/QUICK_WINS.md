# Quick Wins - Easy Enhancements

These are small, high-impact improvements that can be implemented quickly.

## Frontend Quick Wins

### 1. Loading Skeletons ⏱️ 30 min
Replace loading spinners with skeleton screens for better perceived performance.

```typescript
// Add to JobDetail.tsx
{isLoading && (
  <div className="space-y-4">
    <div className="h-8 bg-ink/50 rounded animate-pulse" />
    <div className="h-32 bg-ink/50 rounded animate-pulse" />
  </div>
)}
```

### 2. Keyboard Shortcuts ⌨️ 1 hour
Add keyboard shortcuts for common actions:
- `Cmd/Ctrl + N` - New job
- `Cmd/Ctrl + K` - Search jobs
- `Esc` - Close modals
- `Cmd/Ctrl + /` - Show shortcuts

### 3. Copy-to-Clipboard Everywhere 📋 1 hour
Add copy buttons to:
- Mermaid code (already done)
- TL;DR text (already done)
- Job IDs
- API responses
- Error messages

### 4. Better Empty States 🎨 1 hour
Improve empty states with helpful messages and CTAs:
- "No jobs yet" → "Create your first analysis"
- "No results" → "Processing your content..."

### 5. Toast Improvements 🔔 30 min
- Add success/error icons
- Group related notifications
- Add undo actions where applicable

## Backend Quick Wins

### 6. Better Error Messages 🚨 1 hour
Return actionable error messages:
```python
# Instead of: "Error processing URL"
# Return: "Failed to fetch https://example.com: Connection timeout. Try again or check the URL."
```

### 7. Request Validation 📝 30 min
Add more detailed validation:
- URL format validation
- File size limits
- Content type checks
- Rate limiting per IP

### 8. Health Check Details 💚 30 min
Enhanced health check with service status:
```python
@app.get("/healthz")
async def healthz():
    return {
        "ok": True,
        "version": "0.1.0",
        "uptime": get_uptime(),
        "dependencies": {
            "ingestor": await check_service(INGESTOR_URL),
            "summarize": await check_service(SUMMARIZE_URL),
            "viz": await check_service(VIZ_URL)
        }
    }
```

### 9. Job Expiration 🗑️ 1 hour
Auto-delete old jobs after 30 days:
```python
async def cleanup_old_jobs():
    cutoff = time.time() - (30 * 24 * 60 * 60)
    for job_id, job in list(jobs.items()):
        if job.get("created_at", 0) < cutoff:
            del jobs[job_id]
```

### 10. Request Logging 📊 30 min
Log all requests with timing:
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    log_json("INFO", "Request", 
             method=request.method, 
             path=request.url.path,
             status=response.status_code,
             duration_ms=int(duration * 1000))
    return response
```

## UX Quick Wins

### 11. Job Templates 📑 2 hours
Pre-configured job templates:
- "Research Paper Summary"
- "News Article Analysis"
- "Technical Documentation Review"
- "Competitor Analysis"

### 12. Source Preview 👁️ 2 hours
Show preview of source before processing:
- URL: Show page title and snippet
- PDF: Show first page preview
- Text: Show first 500 characters

### 13. Progress Estimates ⏱️ 1 hour
Show estimated time remaining:
```typescript
const estimatedTime = calculateETA(job.progress, job.created_at)
<p>Estimated time remaining: {estimatedTime}</p>
```

### 14. Job Bookmarks ⭐ 1 hour
Allow users to bookmark/favorite jobs for quick access.

### 15. Export Improvements 📤 1 hour
- Export to Markdown
- Export to CSV (for clusters)
- Batch export multiple jobs

## Developer Experience

### 16. Better Dev Scripts 🛠️ 30 min
Add helper scripts:
```bash
# scripts/dev.sh
#!/bin/bash
# Start all services in background
./scripts/start-services.sh
```

### 17. Environment Validation ✅ 30 min
Validate environment variables on startup:
```python
def validate_env():
    required = ["INGESTOR_URL", "SUMMARIZE_URL", "VIZ_URL"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing env vars: {missing}")
```

### 18. API Examples 📖 1 hour
Add example requests to README:
```bash
# Create job
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d @examples/create-job.json
```

## Performance Quick Wins

### 19. Response Compression 🗜️ 30 min
Add gzip compression:
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 20. Frontend Code Splitting 📦 1 hour
Lazy load routes:
```typescript
const JobDetail = lazy(() => import('./pages/JobDetail'))
const NewJob = lazy(() => import('./pages/NewJob'))
```

---

**Total Estimated Time:** ~20 hours for all quick wins
**High Impact:** Items 1, 2, 6, 11, 12

