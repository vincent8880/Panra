"""
Seed 10 Kenyan-focused prediction markets for March 9–15, 2026.
Run: python manage.py create_kenyan_markets_march2026
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from markets.models import Market

User = get_user_model()


def kenya_eod(year, month, day):
    """End of day Kenya time (EAT = UTC+3) as UTC."""
    # 23:59 EAT = 20:59 UTC same day
    return timezone.make_aware(datetime(year, month, day, 20, 59, 0), timezone=timezone.utc)


class Command(BaseCommand):
    help = 'Create 10 Kenyan prediction markets for March 9–15, 2026'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip markets that already exist (by slug).',
        )

    def handle(self, *args, **options):
        creator = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not creator:
            self.stdout.write(self.style.ERROR('No user found. Create a user first.'))
            return

        markets_data = [
            {
                'title': 'Flood death toll: Will it exceed 40 by March 13?',
                'slug': 'flood-death-toll-kenya-march-2026',
                'question': 'Will the official flood-related death toll in Nairobi/Kenya exceed 40 by end of day Friday March 13, 2026?',
                'description': 'Heavy rains and flood advisories continue. Current reported toll is in the mid-20s; this market resolves YES if the official toll exceeds 40 by end of day March 13.',
                'resolution_criteria': 'Resolves to YES when the official (government or credible authority) flood-related death toll for Nairobi/Kenya is reported as greater than 40 by end of day Friday March 13, 2026.',
                'category': 'News',
                'end_date': kenya_eod(2026, 3, 13),
            },
            {
                'title': 'Major flood relief package by March 12?',
                'slug': 'flood-relief-announcement-march-2026',
                'question': 'Will President Ruto or the government announce a major new flood relief package or compensation framework by Thursday March 12, 2026?',
                'description': 'Amid criticism of the flood response, this market resolves YES if there is a clear new relief or compensation announcement from the government by March 12.',
                'resolution_criteria': 'Resolves to YES when the President or national government publicly announces a major new flood relief package, compensation framework, or equivalent policy (beyond existing directives) by end of day Thursday March 12, 2026.',
                'category': 'News',
                'end_date': kenya_eod(2026, 3, 12),
            },
            {
                'title': 'Cholera or malaria linked to floods by March 15?',
                'slug': 'cholera-malaria-floods-march-2026',
                'question': 'Will the Health Ministry report the first confirmed cholera or malaria cases linked to the floods by March 15, 2026?',
                'description': 'Health alerts have been issued amid contamination risks. This market resolves YES if the Ministry confirms at least one cholera or malaria case attributed to the floods.',
                'resolution_criteria': 'Resolves to YES when the Ministry of Health or equivalent authority publicly reports at least one confirmed cholera or malaria case explicitly linked to the current floods, by end of day March 15, 2026.',
                'category': 'News',
                'end_date': kenya_eod(2026, 3, 15),
            },
            {
                'title': 'IMF/Kenya “advancing” statement by March 13?',
                'slug': 'imf-kenya-statement-march-2026',
                'question': 'By Friday March 13, 2026, will the IMF or Kenya Finance issue any public statement that they are “advancing” toward a new lending program (or a mini-deal before Spring Meetings)?',
                'description': 'IMF mission ended early March with talks continuing. This market resolves YES if either side publicly signals progress toward a new program or a near-term deal by March 13.',
                'resolution_criteria': 'Resolves to YES when the IMF or Kenya’s Ministry of Finance (or National Treasury) makes a public statement by end of day Friday March 13, 2026, indicating that discussions are “advancing” or that they are moving toward a new lending program or a near-term deal.',
                'category': 'Economics',
                'end_date': kenya_eod(2026, 3, 13),
            },
            {
                'title': 'Posta Rangers vs Police: Posta win or draw?',
                'slug': 'posta-rangers-vs-police-march-2026',
                'question': 'In the FKF Premier League clash (Thu/Fri March 12/13), will Posta Rangers win or draw against Police?',
                'description': 'Upcoming FKF Premier League fixture. YES = Posta Rangers win or draw; NO = Police win.',
                'resolution_criteria': 'Resolves to YES when the match result is a Posta Rangers win or a draw. Resolves to NO when Police win. Uses the official FKF/fixture result for the match played on or around March 12–13, 2026.',
                'category': 'Sports',
                'end_date': kenya_eod(2026, 3, 13),
            },
            {
                'title': 'Gor Mahia beat Ulinzi Stars on March 14?',
                'slug': 'gor-mahia-vs-ulinzi-march-14-2026',
                'question': 'Will Gor Mahia beat Ulinzi Stars in the FKF Premier League on Saturday March 14, 2026?',
                'description': 'Big matchup in the round. Resolves on the official full-time result: YES if Gor Mahia win, NO if draw or Ulinzi win.',
                'resolution_criteria': 'Resolves to YES when Gor Mahia win the match (full-time). Resolves to NO when the result is a draw or Ulinzi Stars win. Uses the official FKF result for the fixture on March 14, 2026.',
                'category': 'Sports',
                'end_date': kenya_eod(2026, 3, 14),
            },
            {
                'title': '#SafariRally2026 in top 10 Kenyan X trends?',
                'slug': 'safari-rally-x-trends-march-9-15-2026',
                'question': 'Will #SafariRally2026 (or a related Safari Rally Kenya tag) appear in the top 10 Kenyan X (Twitter) trends at least once between March 9–15, 2026?',
                'description': 'Safari Rally Kenya runs March 12–15; build-up and event buzz could push the tag into Kenyan trends. Resolves YES if it hits top 10 Kenyan trends on any day in the window.',
                'resolution_criteria': 'Resolves to YES when #SafariRally2026 or an agreed equivalent tag (e.g. Safari Rally Kenya, Naivasha WRC) appears in X’s top 10 trends for Kenya on at least one day between March 9 and March 15, 2026 (inclusive). Evidence: screenshot or reputable trend-tracking source.',
                'category': 'Culture',
                'end_date': kenya_eod(2026, 3, 15),
            },
            {
                'title': 'Viral Gachagua/Kindiki Mt Kenya clip: 10k+ likes by March 13?',
                'slug': 'mt-kenya-viral-clip-march-2026',
                'question': 'Will a viral X clip or video of Gachagua or Kindiki from Mt Kenya tours (e.g. Meru, “Bye bye Ruto” echoes) get over 10,000 likes/engagements by March 13, 2026?',
                'description': 'Mt Kenya political tours are in the spotlight. This market resolves YES if any single X post (video/clip) of Gachagua or Kindiki from these tours reaches 10k+ likes (or equivalent engagements as defined) by March 13.',
                'resolution_criteria': 'Resolves to YES when a single X (Twitter) post—video or clip—featuring DP Gachagua or CS Kindiki from their Mt Kenya region tours (e.g. Meru, rallies) reaches 10,000 or more likes (or equivalent engagement metric as agreed) by end of day March 13, 2026.',
                'category': 'Politics',
                'end_date': kenya_eod(2026, 3, 13),
            },
            {
                'title': 'Co-op University Cultural Week top “fun event” on X?',
                'slug': 'coop-university-cultural-week-x-march-2026',
                'question': 'For Co-operative University Cultural Week (March 9–13), will X engagement (mentions/photos) rank it as the top “fun event” of the week vs others by March 15?',
                'description': 'Cultural Week runs March 9–13 (daily from 2:30pm). Resolves YES if by Sunday March 15 it is clearly the most discussed “fun” campus/social event of that week on X in the relevant context.',
                'resolution_criteria': 'Resolves to YES when, by end of day Sunday March 15, 2026, Co-operative University Cultural Week (March 9–13) is verifiably the top “fun event” of the week by X mentions/engagement compared to other similar events (e.g. wellness events, forums) in the same period. Resolution via agreed metric (e.g. hashtag count, mentions).',
                'category': 'Culture',
                'end_date': kenya_eod(2026, 3, 15),
            },
            {
                'title': 'Heavy rainfall advisory extended past March 9?',
                'slug': 'kenya-met-rainfall-advisory-extension-march-2026',
                'question': 'Will Kenya Met extend the heavy rainfall advisory beyond Monday March 9, 2026 (into the next week) for Nairobi metro or other regions?',
                'description': 'Current advisory runs till 7pm March 9. Soils are saturated and flood risks are high. This market resolves YES if the advisory is officially extended to cover any period after March 9.',
                'resolution_criteria': 'Resolves to YES when Kenya Meteorological Department (or equivalent) officially extends the heavy rainfall advisory to include any day(s) after Monday March 9, 2026 (e.g. for Nairobi metro or other specified regions), by end of day March 9 or by the next official update.',
                'category': 'Weather',
                'end_date': kenya_eod(2026, 3, 9),
            },
        ]

        created_count = 0
        skipped = 0
        for data in markets_data:
            slug = data.pop('slug')
            if options.get('skip_existing') and Market.objects.filter(slug=slug).exists():
                skipped += 1
                continue
            market, created = Market.objects.get_or_create(
                slug=slug,
                defaults={
                    **data,
                    'created_by': creator,
                    'status': 'open',
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {market.title}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. Created {created_count} markets' + (f', skipped {skipped} (existing).' if skipped else '.')
            )
        )
