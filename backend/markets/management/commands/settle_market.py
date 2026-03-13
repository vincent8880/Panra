from django.core.management.base import BaseCommand, CommandError

from markets.models import Market
from markets.settlement import settle_market


class Command(BaseCommand):
  help = "Settle a binary market by slug and outcome (yes/no)."

  def add_arguments(self, parser):
    parser.add_argument("slug", type=str, help="Slug of the market to settle")
    parser.add_argument(
      "--outcome",
      type=str,
      required=True,
      choices=["yes", "no"],
      help="Outcome to settle the market as (yes or no)",
    )

  def handle(self, *args, **options):
    slug = options["slug"]
    outcome = options["outcome"]

    try:
      market = Market.objects.get(slug=slug)
    except Market.DoesNotExist:
      raise CommandError(f"Market with slug '{slug}' does not exist.")

    self.stdout.write(self.style.WARNING(f"Settling market '{market.title}' ({slug}) as {outcome.upper()}..."))

    try:
      summary = settle_market(market, outcome, logger=None)
    except ValueError as e:
      raise CommandError(str(e))

    self.stdout.write(
      self.style.SUCCESS(
        f"Done. Users updated: {summary['users_updated']}, total payout: {summary['total_payout']}."
      )
    )

