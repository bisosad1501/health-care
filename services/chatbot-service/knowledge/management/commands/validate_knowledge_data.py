from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from knowledge.models import KnowledgeEntry, DiseaseInformation, SymptomInformation
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate knowledge base data quality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-sources',
            action='store_true',
            help='Check if entries have proper source citations'
        )
        parser.add_argument(
            '--check-medical-review',
            action='store_true', 
            help='Check if entries have medical review'
        )
        parser.add_argument(
            '--check-completeness',
            action='store_true',
            help='Check data completeness'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 Validating Knowledge Base Data Quality...')
        
        issues = []
        
        # Check basic data quality
        issues.extend(self._check_basic_quality())
        
        # Check sources if requested
        if options['check_sources']:
            issues.extend(self._check_sources())
            
        # Check medical review if requested  
        if options['check_medical_review']:
            issues.extend(self._check_medical_review())
            
        # Check completeness if requested
        if options['check_completeness']:
            issues.extend(self._check_completeness())
        
        # Report results
        if issues:
            self.stdout.write(
                self.style.WARNING(f'Found {len(issues)} data quality issues:')
            )
            for issue in issues:
                self.stdout.write(f'  ⚠️  {issue}')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All data quality checks passed!')
            )

    def _check_basic_quality(self):
        """Check basic data quality issues"""
        issues = []
        
        # Check for entries without content
        empty_entries = KnowledgeEntry.objects.filter(
            content__isnull=True
        ).count()
        if empty_entries > 0:
            issues.append(f'{empty_entries} entries have no content')
        
        # Check for very short content
        short_entries = KnowledgeEntry.objects.filter(
            content__length__lt=100
        ).count()
        if short_entries > 0:
            issues.append(f'{short_entries} entries have very short content (<100 chars)')
            
        # Check for missing summaries
        no_summary = KnowledgeEntry.objects.filter(
            summary__isnull=True,
            content_type='ARTICLE'
        ).count()
        if no_summary > 0:
            issues.append(f'{no_summary} articles missing summaries')
            
        return issues

    def _check_sources(self):
        """Check if entries have proper source citations"""
        issues = []
        
        # Check for entries without sources
        no_source = KnowledgeEntry.objects.filter(
            source__isnull=True
        ).count()
        if no_source > 0:
            issues.append(f'{no_source} entries have no source citation')
            
        # Check for entries without author
        no_author = KnowledgeEntry.objects.filter(
            author__isnull=True
        ).count()
        if no_author > 0:
            issues.append(f'{no_author} entries have no author')
            
        return issues

    def _check_medical_review(self):
        """Check medical review status"""
        issues = []
        
        # Check unverified content
        unverified = KnowledgeEntry.objects.filter(
            is_verified=False
        ).count()
        if unverified > 0:
            issues.append(f'{unverified} entries are not medically verified')
            
        # Check low reliability scores
        low_reliability = KnowledgeEntry.objects.filter(
            reliability_score__lt=0.7
        ).count()
        if low_reliability > 0:
            issues.append(f'{low_reliability} entries have low reliability scores (<0.7)')
            
        return issues

    def _check_completeness(self):
        """Check data completeness"""
        issues = []
        
        # Check disease information completeness
        incomplete_diseases = DiseaseInformation.objects.filter(
            symptoms__isnull=True
        ).count()
        if incomplete_diseases > 0:
            issues.append(f'{incomplete_diseases} diseases missing symptom information')
            
        # Check symptom urgency levels
        no_urgency = SymptomInformation.objects.filter(
            urgency_level__isnull=True
        ).count()
        if no_urgency > 0:
            issues.append(f'{no_urgency} symptoms missing urgency level')
            
        # Check for orphaned entries (no category)
        no_category = KnowledgeEntry.objects.filter(
            category__isnull=True
        ).count()
        if no_category > 0:
            issues.append(f'{no_category} entries have no category')
            
        return issues
