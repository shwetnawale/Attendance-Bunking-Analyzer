# Safe Days Feature - User Guide

## What is Safe Days?

The **Safe Days** feature automatically calculates which days you can safely bunk without your attendance dropping below 75%.

## How It Works

### If Your Attendance is ≥75%
When you click **"Find Safe Days"**, the system will:

1. ✅ Calculate all upcoming days (next 30 days) where bunking won't drop you below 75%
2. ✅ Group them by day of week for easy planning
3. ✅ Show you exactly which dates are safe to bunk
4. ✅ Tell you what your final attendance percentage will be

**Example Output:**
```
✅ You can safely bunk 8 days and still stay above 75%!

Monday: Nov 11, Nov 18, Nov 25
Tuesday: Nov 12, Nov 19
Wednesday: Nov 13, Nov 20, Dec 4

If you bunk these 8 days, your attendance will be approximately 75.3%
```

### If Your Attendance is <75%
When you click **"Find Safe Days"**, you'll see a warning:

```
⚠️ Attendance Below 75%

Your current attendance is below 75%. You should focus on 
attending classes instead of bunking. No safe days available.
```

## Using the Feature

### Step 1: Check Your Current Attendance
Look at the **"Current Attendance"** box at the top. If it shows ≥75%, you can use Safe Days.

### Step 2: Click "Find Safe Days"
Click the green **"Find Safe Days"** button to see recommendations.

### Step 3: Review the Plan
The system shows:
- Total number of safe days
- Days grouped by day of week (Monday, Tuesday, etc.)
- Specific dates you can bunk
- Final attendance percentage after bunking

### Step 4: Apply or Close
You have two options:

**Option A: Apply These Days**
- Clicks **"Apply These Days"** button
- All safe days are automatically marked as RED (bunking) on calendar
- Scroll down to see them on the calendar
- Stats boxes update automatically

**Option B: Close**
- Click **"Close"** button
- Returns to normal view
- Nothing is selected

### Step 5: Modify if Needed
After applying, you can:
- Click any red day to change it to green (attending) or clear it
- Click any other day to add more selections
- Stats update in real-time

## Calculation Logic

The system uses this formula for each day:

```
For each upcoming weekday:
  - Assume 4 classes per day (average)
  - Calculate: New % = Current Attended / (Current Total + 4)
  - If New % ≥ 75%, mark as SAFE
```

**Example Calculation:**
```
Current: 215 attended / 308 total = 69.81%

Check Nov 7:
  - New total = 308 + 4 = 312
  - New attended = 215 (not attending this day)
  - New % = 215 / 312 = 68.91%
  - Result: NOT SAFE (below 75%)

Current: 235 attended / 308 total = 76.3%

Check Nov 7:
  - New total = 308 + 4 = 312
  - New attended = 235 (not attending this day)  
  - New % = 235 / 312 = 75.32%
  - Result: SAFE ✅
```

## Smart Features

### 1. Automatically Skips Weekends
Only checks Monday-Friday (assumes no classes on weekends)

### 2. Looks 30 Days Ahead
Checks the next month to give you planning flexibility

### 3. Groups by Day of Week
Makes it easy to see patterns:
- "I can bunk all Mondays this month!"
- "Wednesday is my safe bunking day"

### 4. Shows Final Percentage
You know exactly what your attendance will be after bunking

### 5. One-Click Apply
Don't manually select 8 days - just click "Apply These Days"!

## Tips for Best Results

### Tip 1: Use When Attendance is Higher
- At 80%: More safe days available
- At 75.5%: Limited safe days
- At 75%: Very few or no safe days

### Tip 2: Plan Ahead
- Use Safe Days at the start of the month
- Gives you better planning options
- Can coordinate with friends

### Tip 3: Leave Buffer
- Don't use ALL safe days
- Keep 1-2 days as emergency buffer
- Unexpected events happen!

### Tip 4: Check Regularly
- Run Safe Days calculator weekly
- Your attendance changes as you attend/bunk
- New safe days may become available

### Tip 5: Combine with Manual Selection
- Use Safe Days as starting point
- Manually adjust green/red as needed
- Fine-tune your plan

## Example Scenarios

### Scenario 1: Good Attendance (80%)
```
Current: 246/308 = 80%

Find Safe Days Results:
✅ You can safely bunk 12 days!

Monday: Nov 11, 18, 25, Dec 2, 9
Tuesday: Nov 12, 19, 26
Wednesday: Nov 13, 20
Thursday: Nov 14, 21

Final: ~75.8%
```

### Scenario 2: Borderline Attendance (75.5%)
```
Current: 232/308 = 75.3%

Find Safe Days Results:
✅ You can safely bunk 3 days!

Monday: Nov 11
Wednesday: Nov 13  
Friday: Nov 15

Final: ~75.1%
```

### Scenario 3: Below Threshold (72%)
```
Current: 222/308 = 72.1%

Find Safe Days Results:
⚠️ Attendance Below 75%
No safe days available.
Focus on attending classes!
```

## Troubleshooting

### "No safe days available" but attendance is above 75%
- Your attendance might be too close to 75% (like 75.1%)
- Even one bunk would drop you below
- Try attending more classes first

### Safe days showing wrong dates
- Refresh the page
- Make sure your current attendance is correct
- Check if you already have selections

### Applied safe days but want to change
- Just click on any red day to cycle through:
  - Red → Clear → Green → Red
- Stats update automatically

## Button Colors Guide

- 🟢 **Green Button** "Find Safe Days" - Click to calculate
- 🟢 **Green Button** "Apply These Days" - Auto-select safe days  
- 🟡 **Yellow Button** "Close" - Close the panel
- 🔴 **Red Warning** - Attendance below 75%

---

## Summary

Safe Days is your smart bunking assistant that:
- ✅ Only works when attendance ≥75%
- ✅ Calculates safe bunking days automatically
- ✅ Groups by day of week
- ✅ Shows final attendance percentage
- ✅ One-click apply to calendar
- ✅ Warns you if attendance too low

Use it wisely to plan your bunks without risking attendance! 🎯
