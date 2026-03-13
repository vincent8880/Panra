from decimal import Decimal
from typing import Literal, Optional

from django.db import transaction
from django.utils import timezone

from markets.models import Market
from trading.models import Position

OutcomeType = Literal["yes", "no"]


def settle_market(market: Market, outcome: OutcomeType, logger: Optional[object] = None) -> dict:
  """
  Core settlement logic for a binary market.

  - Marks the market as resolved (YES/NO)
  - Pays out winners (1 credit per winning share)
  - Clears positions in that market
  - Updates user stats and points via User.update_stats_after_market_resolution

  Returns a summary dict for logging / admin messages.
  """
  from users.models import User  # Local import to avoid circulars

  if outcome not in ("yes", "no"):
    raise ValueError("Outcome must be 'yes' or 'no'")

  if market.status == "resolved":
    raise ValueError(f"Market '{market.slug}' is already resolved.")

  summary = {
    "market": market.slug,
    "outcome": outcome,
    "users_updated": 0,
    "total_payout": Decimal("0.00"),
  }

  with transaction.atomic():
    positions = Position.objects.select_for_update().filter(market=market)

    # If no one traded, just resolve the market and exit.
    if not positions.exists():
      market.status = "resolved"
      market.resolution = outcome
      market.resolution_date = timezone.now()
      market.save(update_fields=["status", "resolution", "resolution_date"])
      return summary

    for position in positions:
      user: User = position.user

      winning_shares = position.yes_shares if outcome == "yes" else position.no_shares
      losing_shares = position.no_shares if outcome == "yes" else position.yes_shares

      payout = winning_shares  # 1 credit per winning share
      was_correct = winning_shares > 0

      # Credit winners
      if payout > 0:
        from users.models import User as UserModel  # type: ignore

        # Use the user's helper so decay/regen fields stay consistent
        user.update_credits_from_trade(payout)
        summary["total_payout"] += payout

      # Update stats (win/loss, accuracy, streak, ROI, points)
      user.update_stats_after_market_resolution(market, was_correct)
      summary["users_updated"] += 1

      # Clear the position in this market (no more open exposure after resolution)
      position.yes_shares = Decimal("0.00")
      position.no_shares = Decimal("0.00")
      position.yes_avg_cost = Decimal("0.0000")
      position.no_avg_cost = Decimal("0.0000")
      position.save(update_fields=["yes_shares", "no_shares", "yes_avg_cost", "no_avg_cost", "updated_at"])

    # Finally, mark the market as resolved
    market.status = "resolved"
    market.resolution = outcome
    market.resolution_date = timezone.now()
    market.save(update_fields=["status", "resolution", "resolution_date"])

  if logger:
    logger.info(
      f"[settle_market] Market {market.slug} resolved as {outcome}. "
      f"Users updated: {summary['users_updated']}, total payout: {summary['total_payout']}"
    )

  return summary

