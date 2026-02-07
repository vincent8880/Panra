# Practice Credits System

## Overview
The platform uses a **Practice Credits** system (not real money) to allow users to trade prediction markets without regulatory concerns. Credits have two key mechanics:

1. **Decay**: Credits decrease if you don't use them (encourages daily engagement)
2. **Regeneration**: Credits slowly regenerate if you lose them (prevents instant re-betting)

## Credit Mechanics

### Starting Credits
- **10,000 credits** for all new users
- Maximum cap: **10,000 credits** (can be adjusted per user)

### Decay System (Use It or Lose It)
- **Rate**: 1% per day OR minimum 100 credits per day (whichever is higher)
- **Trigger**: If user hasn't made a trade in 24+ hours
- **Purpose**: Encourages daily engagement and active trading

**Example:**
- User has 10,000 credits, hasn't traded in 2 days
- Decay: 10,000 × 0.01 × 2 = 200 credits lost
- New balance: 9,800 credits

### Regeneration System (Slow Recovery)
- **Rate**: 100 credits per hour
- **Trigger**: When credits are below the base amount (after losses)
- **Purpose**: Prevents users from instantly re-betting after losses

**Example:**
- User loses and has 5,000 credits
- Regenerates 100 credits/hour
- Takes 50 hours to get back to 10,000 credits

### Trade Activity
- When a user makes a trade, `last_activity_at` is updated
- This resets the decay timer
- Credits are deducted/added based on trade outcomes

## API Endpoints

### Get Current User Credits
```
GET /api/auth/users/me/
```
Returns:
```json
{
  "credits": 10000.00,
  "current_credits": 9500.00,  // After decay/regeneration calculation
  "credit_status": {
    "current": 9500.00,
    "stored": 10000.00,
    "max": 10000.00,
    "days_inactive": 0.5,
    "next_decay_at": "2024-01-20T12:00:00Z",
    "regenerating": false,
    "hours_to_full_regen": null,
    "regen_rate_per_hour": 100.00
  }
}
```

### Get Credits Status Only
```
GET /api/auth/users/credits/
```

## Database Fields

### User Model
- `credits`: Stored credit balance (default: 10,000)
- `last_activity_at`: Last trade timestamp (auto-updated)
- `base_credits`: Base amount for regeneration calculation
- `max_credits`: Maximum credits cap (default: 10,000)

## Calculation Logic

The `get_current_credits()` method calculates the effective balance:

1. **Apply Decay**: If inactive, reduce credits based on days inactive
2. **Apply Regeneration**: If below base, add credits based on hours since last activity
3. **Return**: Current effective balance

## Frontend Integration

The frontend should:
1. Display "Practice Credits" (not "KES" or "Money")
2. Show current credits with decay/regeneration status
3. Display countdown timers for next decay/regeneration
4. Warn users about decay if inactive

## Future Enhancements

- Daily login bonuses
- Referral rewards
- Achievement bonuses
- Leaderboard prizes (all in credits, not real money)

































