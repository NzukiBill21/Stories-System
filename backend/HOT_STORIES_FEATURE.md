# Hot Stories Feature - Early Trend Detection for Kenya

## Overview

This feature enables you to catch **hot stories for Kenya before they blow up** by detecting emerging trends with high engagement velocity.

## Key Features

### 1. Hot/Emerging Stories Endpoint

**Endpoint:** `GET /api/stories/hot`

**Parameters:**
- `limit` (default: 30) - Maximum number of stories
- `is_kenyan` (optional) - Filter Kenyan stories only
- `hours_back` (default: 6) - Look back window (shorter = more recent trends)

**How it works:**
- Filters stories from the last 6 hours (configurable)
- Requires minimum engagement velocity of 20/hour (trending NOW)
- Orders by engagement velocity DESC (hottest first)
- Prioritizes Kenyan content

**Example:**
```bash
# All hot stories
GET /api/stories/hot

# Hot Kenyan stories only
GET /api/stories/hot?is_kenyan=true

# Hot stories from last 3 hours
GET /api/stories/hot?hours_back=3&is_kenyan=true
```

### 2. Lower Thresholds for Kenyan Content

Kenyan stories now have **lower thresholds** to catch early trends:

- **Score threshold:** 30% lower (21 instead of 30)
- **Velocity threshold:** 50% lower (2.5/hour instead of 5/hour)

This means Kenyan stories are caught earlier, before they become viral.

### 3. Frontend Hot Stories Toggle

**Location:** Filter Panel → "Hot/Emerging Stories" toggle

**Features:**
- Toggle to show only hot/emerging stories
- Shows stories from last 6 hours with high engagement velocity
- Auto-refreshes every 2 minutes (vs 5 minutes for regular stories)
- Can be combined with "Kenyan Stories Only" filter

### 4. Kenyan Stories Only Filter

**Location:** Filter Panel → "Kenyan Stories Only" toggle

**Features:**
- Filter to show only Kenyan content
- Works with both regular and hot stories
- Visual badge indicator (🇰🇪)

## Usage

### Via API

```bash
# Get hot Kenyan stories
curl "http://localhost:8000/api/stories/hot?is_kenyan=true&limit=30"

# Get all hot stories from last 3 hours
curl "http://localhost:8000/api/stories/hot?hours_back=3"
```

### Via Frontend

1. Open the dashboard
2. Click the filter icon (top right)
3. Toggle "Hot/Emerging Stories" ON
4. Optionally toggle "Kenyan Stories Only" ON
5. Stories will auto-refresh every 2 minutes

## Technical Details

### Engagement Velocity Calculation

```
engagement_velocity = (likes + comments*2 + shares*3 + views*0.1) / hours_since_posted
```

### Hot Stories Criteria

- `engagement_velocity >= 20.0` (trending NOW)
- `posted_at >= (now - hours_back)`
- Ordered by: `engagement_velocity DESC`, then `is_kenyan DESC`, then `score DESC`

### Kenyan Content Boost

In `scoring.py`, `should_keep_post()` now accepts `is_kenyan` parameter:

```python
# Lower thresholds for Kenyan content
min_score = settings.min_engagement_score * (0.7 if is_kenyan else 1.0)  # 30% lower
min_velocity = settings.min_engagement_velocity * (0.5 if is_kenyan else 1.0)  # 50% lower
```

## Benefits

✅ **Early Detection** - Catch stories before they go viral  
✅ **Kenyan-Focused** - Lower thresholds for Kenyan content  
✅ **Real-Time** - Updates every 2 minutes for hot stories  
✅ **High Quality** - Only shows stories with high engagement velocity  
✅ **Easy to Use** - Simple toggle in the filter panel  

## Configuration

### Adjust Hot Stories Threshold

Edit `backend/api.py`:

```python
# In get_hot_stories endpoint
query = query.filter(Story.engagement_velocity >= 20.0)  # Change this value
```

### Adjust Time Window

Edit `backend/api.py`:

```python
hours_back: int = Query(6, ge=1, le=24)  # Change default from 6 to your preference
```

### Adjust Kenyan Thresholds

Edit `backend/scoring.py`:

```python
# In should_keep_post function
min_score = settings.min_engagement_score * (0.7 if is_kenyan else 1.0)  # Adjust 0.7
min_velocity = settings.min_engagement_velocity * (0.5 if is_kenyan else 1.0)  # Adjust 0.5
```

## Monitoring

Check hot stories in database:

```sql
-- Hot Kenyan stories (last 6 hours, velocity >= 20)
SELECT 
    headline,
    platform,
    engagement_velocity,
    score,
    posted_at,
    TIMESTAMPDIFF(HOUR, posted_at, NOW()) as hours_ago
FROM stories
WHERE is_kenyan = 1
  AND is_active = 1
  AND engagement_velocity >= 20.0
  AND posted_at >= DATE_SUB(NOW(), INTERVAL 6 HOUR)
ORDER BY engagement_velocity DESC
LIMIT 30;
```

## Next Steps

1. **Increase scraping frequency** for Kenyan sources (currently 15-60 min)
2. **Add more Kenyan social media sources** (X/Twitter, Facebook pages)
3. **Add alerts** for very high velocity stories
4. **Add trending keywords detection** for early topic identification


