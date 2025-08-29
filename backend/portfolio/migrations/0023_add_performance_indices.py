# Generated migration for database optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0022_project_original_filename_and_more'),
    ]

    operations = [
        # Add database indices for better query performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_order_date ON portfolio_project (\"order\", project_date DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_order_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_service_order_name ON portfolio_service (\"order\", name);", 
            reverse_sql="DROP INDEX IF EXISTS idx_service_order_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_image_project_order ON portfolio_projectimage (project_id, \"order\");",
            reverse_sql="DROP INDEX IF EXISTS idx_project_image_project_order;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_service_image_service_order ON portfolio_serviceimage (service_id, \"order\");",
            reverse_sql="DROP INDEX IF EXISTS idx_service_image_service_order;"
        ),
    ]
