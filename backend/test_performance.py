import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project
from django.db import connection

print("Testing optimized queries...")

# Reset connection queries
connection.queries_log.clear()

# Test the optimized query
projects = Project.objects.select_related().prefetch_related(
    'categories', 'subcategories', 'album_images'
).annotate(
    album_images_count_annotated=django.db.models.Count('album_images')
)[:5]

# Force evaluation to trigger queries
project_list = list(projects)

print(f'Number of projects fetched: {len(project_list)}')
print(f'Number of queries executed: {len(connection.queries)}')

print('\nQuery details:')
for i, query in enumerate(connection.queries, 1):
    sql = query['sql']
    time = query['time']
    print(f'{i}. Time: {time}s - {sql[:100]}...')

# Test serialization performance
print('\nTesting serialization...')
connection.queries_log.clear()

from portfolio.serializers import ProjectSerializer
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/')

serializer = ProjectSerializer(project_list, many=True, context={'request': request})
data = serializer.data

print(f'Serialization queries: {len(connection.queries)}')
print(f'Serialized {len(data)} projects')

for i, query in enumerate(connection.queries, 1):
    sql = query['sql']
    time = query['time']
    print(f'{i}. Time: {time}s - {sql[:100]}...')
