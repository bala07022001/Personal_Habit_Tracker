# PostgreSQL Hands-On Learning Guide
# Run these queries in your Query Editor page to learn SQL!

## 🎯 Learning Goals
By running these queries, you'll learn:
- SELECT and filtering
- Joins and relationships
- Aggregation and grouping
- Window functions
- Common Table Expressions (CTEs)
- Date/time operations

---

## 📖 Chapter 1: Basic Queries

### Query 1.1: See all your habits
```sql
SELECT * FROM habits WHERE status = 'active';
```
**What it does:** Lists all active habits
**Learning:** WHERE clause filters results

---

### Query 1.2: Count habits by category
```sql
SELECT category, COUNT(*) as habit_count
FROM habits
WHERE status = 'active'
GROUP BY category
ORDER BY habit_count DESC;
```
**What it does:** Groups habits by category and counts them
**Learning:** GROUP BY aggregates rows, COUNT() counts matches

---

### Query 1.3: Find your most logged habit
```sql
SELECT 
    h.name,
    COUNT(hl.id) as log_count,
    MAX(hl.log_date) as last_logged
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
WHERE h.status = 'active'
GROUP BY h.id, h.name
ORDER BY log_count DESC
LIMIT 1;
```
**What it does:** Shows your most logged habit
**Learning:** 
- LEFT JOIN: keeps all habits even if no logs
- COUNT: counts related records
- LIMIT 1: get only the top result

---

## 📈 Chapter 2: Time-Based Queries

### Query 2.1: Last 7 days of habit logging
```sql
SELECT 
    h.name,
    hl.log_date,
    hl.value,
    h.unit
FROM habits h
JOIN habit_log hl ON h.id = hl.habit_id
WHERE hl.log_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY hl.log_date DESC, h.name;
```
**What it does:** Shows all logs from the past week
**Learning:**
- CURRENT_DATE: today's date
- INTERVAL: add/subtract time
- INNER JOIN: only show habits with logs

---

### Query 2.2: Daily completion rate (last 30 days)
```sql
SELECT
    EXTRACT(DATE FROM hl.log_date) as date,
    COUNT(DISTINCT h.id) as habits_logged,
    (SELECT COUNT(*) FROM habits WHERE status = 'active') as total_habits,
    ROUND(100.0 * COUNT(DISTINCT h.id) / 
          (SELECT COUNT(*) FROM habits WHERE status = 'active'), 1) as completion_pct
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
WHERE hl.log_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY EXTRACT(DATE FROM hl.log_date)
ORDER BY date DESC;
```
**What it does:** Shows what % of habits you logged each day
**Learning:**
- EXTRACT: get specific part of date
- Subqueries: nest queries inside
- Calculation: do math on columns

---

## 🎯 Chapter 3: Habit Performance

### Query 3.1: Average daily values by habit (30 days)
```sql
SELECT
    h.name,
    h.action_type,
    h.unit,
    h.target_value,
    COUNT(hl.id) as days_logged,
    SUM(hl.value) as total,
    ROUND(AVG(hl.value), 2) as daily_avg,
    CASE 
        WHEN h.target_value > 0 
        THEN ROUND(100.0 * AVG(hl.value) / h.target_value, 1)
        ELSE 0
    END as achievement_pct
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id 
    AND hl.log_date >= CURRENT_DATE - INTERVAL '30 days'
WHERE h.status = 'active'
GROUP BY h.id, h.name, h.action_type, h.unit, h.target_value
ORDER BY achievement_pct DESC;
```
**What it does:** Shows performance vs targets for each habit
**Learning:**
- SUM: add up values
- AVG: calculate average
- CASE/WHEN: conditional logic (if/then)
- Calculations: divide for percentages

---

### Query 3.2: Habit trends (is it improving?)
```sql
SELECT
    h.name,
    COUNT(DISTINCT 
        CASE 
            WHEN hl.log_date >= CURRENT_DATE - INTERVAL '7 days'
            THEN hl.id 
        END
    ) as this_week_count,
    COUNT(DISTINCT 
        CASE 
            WHEN hl.log_date >= CURRENT_DATE - INTERVAL '14 days'
            AND hl.log_date < CURRENT_DATE - INTERVAL '7 days'
            THEN hl.id 
        END
    ) as last_week_count,
    CASE
        WHEN COUNT(DISTINCT 
            CASE 
                WHEN hl.log_date >= CURRENT_DATE - INTERVAL '14 days'
                AND hl.log_date < CURRENT_DATE - INTERVAL '7 days'
                THEN hl.id 
            END
        ) > 0
        THEN ROUND(100.0 * (COUNT(DISTINCT 
            CASE 
                WHEN hl.log_date >= CURRENT_DATE - INTERVAL '7 days'
                THEN hl.id 
            END
        ) - COUNT(DISTINCT 
            CASE 
                WHEN hl.log_date >= CURRENT_DATE - INTERVAL '14 days'
                AND hl.log_date < CURRENT_DATE - INTERVAL '7 days'
                THEN hl.id 
            END
        )) / COUNT(DISTINCT 
            CASE 
                WHEN hl.log_date >= CURRENT_DATE - INTERVAL '14 days'
                AND hl.log_date < CURRENT_DATE - INTERVAL '7 days'
                THEN hl.id 
            END
        ), 1)
        ELSE 0
    END as trend_pct
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
WHERE h.status = 'active'
GROUP BY h.id, h.name
ORDER BY trend_pct DESC;
```
**What it does:** Compares this week vs last week to show trends
**Learning:** Advanced CASE/WHEN for comparisons

---

## 📚 Chapter 4: Reading & Ideas

### Query 4.1: Books with most ideas captured
```sql
SELECT
    b.title,
    b.author,
    COUNT(i.id) as idea_count,
    COUNT(a.id) as applications,
    b.status
FROM books b
LEFT JOIN ideas i ON b.id = i.book_id
LEFT JOIN applications a ON i.id = a.idea_id
GROUP BY b.id, b.title, b.author, b.status
HAVING COUNT(i.id) > 0
ORDER BY idea_count DESC;
```
**What it does:** Shows which books have given you the most ideas
**Learning:**
- HAVING: filter after GROUP BY
- Multiple JOINs: connect 3+ tables

---

### Query 4.2: Ideas waiting to be applied
```sql
SELECT
    i.id,
    i.title,
    b.title as book_title,
    i.chapter_section,
    i.captured_date,
    COUNT(a.id) as applications
FROM ideas i
LEFT JOIN books b ON i.book_id = b.id
LEFT JOIN applications a ON i.id = a.idea_id
WHERE i.status = 'captured'
GROUP BY i.id, b.title
ORDER BY i.captured_date DESC;
```
**What it does:** Shows all ideas you haven't applied yet
**Learning:** LEFT JOIN preserves all ideas even if not applied

---

## 🚀 Chapter 5: Advanced - Window Functions

### Query 5.1: Rank habits by consistency
```sql
SELECT
    h.name,
    h.status,
    COUNT(hl.id) as total_logs,
    COUNT(DISTINCT DATE_TRUNC('week', hl.log_date)) as weeks_active,
    ROW_NUMBER() OVER (ORDER BY COUNT(hl.id) DESC) as rank,
    ROUND(100.0 * COUNT(hl.id) / 
        MAX(COUNT(hl.id)) OVER (), 1) as consistency_score
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
GROUP BY h.id, h.name, h.status
ORDER BY total_logs DESC;
```
**What it does:** Ranks habits by total logs, shows consistency
**Learning:**
- ROW_NUMBER() OVER: window function for ranking
- MAX() OVER: window function to get max across all rows

---

### Query 5.2: Daily habit ranking
```sql
SELECT
    log_date,
    name,
    value,
    RANK() OVER (PARTITION BY log_date ORDER BY value DESC) as daily_rank
FROM (
    SELECT
        hl.log_date,
        h.name,
        hl.value
    FROM habits h
    JOIN habit_log hl ON h.id = hl.habit_id
    WHERE hl.log_date >= CURRENT_DATE - INTERVAL '7 days'
) daily_logs
ORDER BY log_date DESC, daily_rank;
```
**What it does:** For each day, ranks habits by value logged
**Learning:**
- PARTITION BY: window function with groups
- Subqueries: use query results as a table

---

## 🎓 Chapter 6: Common Table Expressions (CTEs)

### Query 6.1: Comprehensive habit analysis
```sql
WITH habit_stats AS (
    SELECT
        h.id,
        h.name,
        h.category,
        COUNT(hl.id) as total_logs,
        AVG(hl.value) as avg_value,
        MAX(hl.log_date) as last_logged
    FROM habits h
    LEFT JOIN habit_log hl ON h.id = hl.habit_id
    WHERE h.status = 'active'
    GROUP BY h.id, h.name, h.category
),
habit_ranking AS (
    SELECT
        id,
        name,
        category,
        total_logs,
        avg_value,
        last_logged,
        ROW_NUMBER() OVER (ORDER BY total_logs DESC) as rank
    FROM habit_stats
)
SELECT * FROM habit_ranking WHERE rank <= 10;
```
**What it does:** Multi-step analysis: first calculate stats, then rank
**Learning:**
- WITH: define temporary tables
- Break complex queries into readable steps

---

## 🔍 Chapter 7: Debugging & Optimization

### Query 7.1: See table sizes
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```
**What it does:** Shows which tables are largest
**Learning:** System tables give metadata about your database

---

### Query 7.2: See index effectiveness
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```
**What it does:** Shows which indexes are being used
**Learning:** Indexes help find data fast!

---

## 📝 Writing Your Own Queries

### Exercise 1: Total time spent on habits
Create a query that calculates total hours spent on all 'duration' type habits

```sql
-- SOLUTION (try to write it first!):
SELECT
    h.name,
    h.unit,
    SUM(hl.value) as total_time
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
WHERE h.action_type = 'duration'
GROUP BY h.id, h.name, h.unit
ORDER BY total_time DESC;
```

---

### Exercise 2: Most consistent day of week
Find which day of the week you log most habits

```sql
-- SOLUTION:
SELECT
    TO_CHAR(hl.log_date, 'Day') as day_of_week,
    COUNT(DISTINCT h.id) as habits_logged,
    COUNT(hl.id) as total_logs
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
GROUP BY TO_CHAR(hl.log_date, 'Day')
ORDER BY habits_logged DESC;
```

---

## 🎯 Next: Try These in Query Editor

1. Copy a query from above
2. Paste into the Query Editor page in Streamlit
3. Run it and see results
4. Modify it to try your own variations
5. Read the results and understand what each column means

**Happy learning!** 🚀
