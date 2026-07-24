from django.db import migrations

ADD_COLUMN_SQL = """
ALTER TABLE resumes_resume
    ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone
    NOT NULL DEFAULT NOW();

ALTER TABLE resumes_resume
    ALTER COLUMN updated_at DROP DEFAULT;
"""


class Migration(migrations.Migration):
    """
    Repairs schema drift: 0001_initial declared `updated_at` and is recorded
    as applied, but the column is absent from the database. Django's
    autodetector only diffs models against migration STATE, so it can never
    detect or heal this. We patch the physical table only, and declare
    state_operations=[] because 0001_initial already put the field in state.
    """

    dependencies = [
        ("resumes", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=ADD_COLUMN_SQL,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[],
        ),
    ]