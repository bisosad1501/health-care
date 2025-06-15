from django.core.management.base import BaseCommand
from django.db import transaction
from knowledge.models import (
    KnowledgeCategory, KnowledgeEntry, KnowledgeTag, 
    DiseaseInformation, SymptomInformation, MedicalTerm
)
import json
import os


class Command(BaseCommand):
    help = 'Load sample knowledge base data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-file',
            type=str,
            help='Path to JSON data file',
            default='knowledge/fixtures/sample_knowledge_data.json'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        data_file = options['data_file']
        clear_existing = options['clear_existing']

        if not os.path.exists(data_file):
            self.stdout.write(
                self.style.ERROR(f'Data file not found: {data_file}')
            )
            return

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading data file: {str(e)}')
            )
            return

        if clear_existing:
            self.stdout.write('Clearing existing data...')
            self._clear_existing_data()

        self.stdout.write('Loading knowledge base data...')
        
        with transaction.atomic():
            # Load categories
            categories = self._load_categories(data.get('categories', []))
            
            # Load tags
            tags = self._load_tags(data.get('tags', []))
            
            # Load medical terms
            terms = self._load_medical_terms(data.get('medical_terms', []), categories)
            
            # Load symptoms
            symptoms = self._load_symptoms(data.get('symptoms', []), categories)
            
            # Load diseases
            diseases = self._load_diseases(data.get('diseases', []), categories, symptoms)
            
            # Load knowledge entries
            entries = self._load_knowledge_entries(data.get('knowledge_entries', []), categories, tags)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded:\n'
                f'- {len(categories)} categories\n'
                f'- {len(tags)} tags\n'
                f'- {len(terms)} medical terms\n'
                f'- {len(symptoms)} symptoms\n'
                f'- {len(diseases)} diseases\n'
                f'- {len(entries)} knowledge entries'
            )
        )

    def _clear_existing_data(self):
        """Clear existing knowledge base data"""
        KnowledgeEntry.objects.all().delete()
        DiseaseInformation.objects.all().delete()
        SymptomInformation.objects.all().delete()
        MedicalTerm.objects.all().delete()
        KnowledgeTag.objects.all().delete()
        KnowledgeCategory.objects.all().delete()

    def _load_categories(self, categories_data):
        """Load knowledge categories"""
        categories = {}
        
        for cat_data in categories_data:
            category = KnowledgeCategory.objects.create(
                name=cat_data['name'],
                category_type=cat_data['category_type'],
                description=cat_data.get('description', ''),
                is_active=cat_data.get('is_active', True)
            )
            categories[cat_data['name']] = category
            self.stdout.write(f'  Created category: {category.name}')
        
        return categories

    def _load_tags(self, tags_data):
        """Load knowledge tags"""
        tags = {}
        
        for tag_data in tags_data:
            tag = KnowledgeTag.objects.create(
                name=tag_data['name'],
                description=tag_data.get('description', ''),
                color=tag_data.get('color', '#007bff'),
                is_active=tag_data.get('is_active', True)
            )
            tags[tag_data['name']] = tag
            self.stdout.write(f'  Created tag: {tag.name}')
        
        return tags

    def _load_medical_terms(self, terms_data, categories):
        """Load medical terms"""
        terms = {}
        
        for term_data in terms_data:
            category = categories.get(term_data['category'])
            if not category:
                self.stdout.write(
                    self.style.WARNING(f'Category not found: {term_data["category"]}')
                )
                continue
            
            term = MedicalTerm.objects.create(
                term=term_data['term'],
                definition=term_data['definition'],
                vietnamese_term=term_data.get('vietnamese_term'),
                pronunciation=term_data.get('pronunciation'),
                synonyms=term_data.get('synonyms', ''),
                category=category,
                is_active=term_data.get('is_active', True)
            )
            terms[term_data['term']] = term
            self.stdout.write(f'  Created term: {term.term}')
        
        return terms

    def _load_symptoms(self, symptoms_data, categories):
        """Load symptom information"""
        symptoms = {}
        
        for symptom_data in symptoms_data:
            category = categories.get(symptom_data['category'])
            if not category:
                self.stdout.write(
                    self.style.WARNING(f'Category not found: {symptom_data["category"]}')
                )
                continue
            
            symptom = SymptomInformation.objects.create(
                name=symptom_data['name'],
                description=symptom_data['description'],
                body_part=symptom_data.get('body_part'),
                urgency_level=symptom_data.get('urgency_level', 'LOW'),
                possible_causes=symptom_data.get('possible_causes'),
                when_to_see_doctor=symptom_data.get('when_to_see_doctor'),
                home_remedies=symptom_data.get('home_remedies'),
                category=category,
                is_active=symptom_data.get('is_active', True)
            )
            symptoms[symptom_data['name']] = symptom
            self.stdout.write(f'  Created symptom: {symptom.name}')
        
        return symptoms

    def _load_diseases(self, diseases_data, categories, symptoms):
        """Load disease information"""
        diseases = {}
        
        for disease_data in diseases_data:
            category = categories.get(disease_data['category'])
            if not category:
                self.stdout.write(
                    self.style.WARNING(f'Category not found: {disease_data["category"]}')
                )
                continue
            
            disease = DiseaseInformation.objects.create(
                name=disease_data['name'],
                icd_code=disease_data.get('icd_code'),
                description=disease_data['description'],
                causes=disease_data.get('causes'),
                symptoms=disease_data.get('symptoms'),
                diagnosis=disease_data.get('diagnosis'),
                treatment=disease_data.get('treatment'),
                prevention=disease_data.get('prevention'),
                complications=disease_data.get('complications'),
                prognosis=disease_data.get('prognosis'),
                severity_level=disease_data.get('severity_level', 'MILD'),
                is_contagious=disease_data.get('is_contagious', False),
                is_chronic=disease_data.get('is_chronic', False),
                category=category,
                is_active=disease_data.get('is_active', True)
            )
            
            # Add related symptoms
            if 'related_symptoms' in disease_data:
                for symptom_name in disease_data['related_symptoms']:
                    symptom = symptoms.get(symptom_name)
                    if symptom:
                        disease.related_diseases.add(symptom)
            
            diseases[disease_data['name']] = disease
            self.stdout.write(f'  Created disease: {disease.name}')
        
        return diseases

    def _load_knowledge_entries(self, entries_data, categories, tags):
        """Load knowledge entries"""
        entries = {}
        
        for entry_data in entries_data:
            category = categories.get(entry_data['category'])
            if not category:
                self.stdout.write(
                    self.style.WARNING(f'Category not found: {entry_data["category"]}')
                )
                continue
            
            entry = KnowledgeEntry.objects.create(
                title=entry_data['title'],
                content=entry_data['content'],
                summary=entry_data.get('summary'),
                category=category,
                content_type=entry_data.get('content_type', 'ARTICLE'),
                difficulty_level=entry_data.get('difficulty_level', 'BASIC'),
                keywords=entry_data.get('keywords', ''),
                author=entry_data.get('author'),
                source=entry_data.get('source'),
                reliability_score=entry_data.get('reliability_score', 1.0),
                is_active=entry_data.get('is_active', True),
                is_verified=entry_data.get('is_verified', False)
            )
            
            # Add tags
            if 'tags' in entry_data:
                for tag_name in entry_data['tags']:
                    tag = tags.get(tag_name)
                    if tag:
                        entry.tags.add(tag)
            
            entries[entry_data['title']] = entry
            self.stdout.write(f'  Created entry: {entry.title}')
        
        return entries
