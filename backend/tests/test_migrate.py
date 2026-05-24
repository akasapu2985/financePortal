from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from db.migrate import get_migration_files, get_migrations_path

ROOT = Path(__file__).resolve().parents[2]
SCRATCH_ROOT = ROOT / 'backend' / 'tests' / '_scratch'


class MigrationDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work_dir = SCRATCH_ROOT / self._testMethodName
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
        self.work_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)

    def test_get_migration_files_returns_numeric_order(self) -> None:
        migrations_dir = self.work_dir / 'migrations'
        migrations_dir.mkdir()
        (migrations_dir / '010_last.sql').write_text('SELECT 3;', encoding='utf-8')
        (migrations_dir / '001_first.sql').write_text('SELECT 1;', encoding='utf-8')
        (migrations_dir / '002_second.sql').write_text('SELECT 2;', encoding='utf-8')
        (migrations_dir / 'notes.txt').write_text('ignore me', encoding='utf-8')

        migration_files = get_migration_files(migrations_dir)

        self.assertEqual(
            [migration_file.name for migration_file in migration_files],
            ['001_first.sql', '002_second.sql', '010_last.sql'],
        )

    def test_get_migrations_path_points_to_sql_directory(self) -> None:
        migrations_path = get_migrations_path()

        self.assertTrue(migrations_path.is_dir())
        self.assertTrue((migrations_path / '001_core.sql').exists())
        self.assertTrue((migrations_path / '002_news.sql').exists())
        self.assertTrue((migrations_path / '003_watchlists.sql').exists())


if __name__ == '__main__':
    unittest.main()
