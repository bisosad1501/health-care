from django.core.management.base import BaseCommand
from knowledge.services import KnowledgeSearchEngine


class Command(BaseCommand):
    help = 'Build search index for knowledge base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Force rebuild the entire index'
        )

    def handle(self, *args, **options):
        self.stdout.write('Building knowledge base search index...')
        
        search_engine = KnowledgeSearchEngine()
        
        try:
            search_engine.build_search_index()
            self.stdout.write(
                self.style.SUCCESS('Successfully built search index!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error building search index: {str(e)}')
            )
