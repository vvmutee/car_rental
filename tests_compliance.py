"""Автоматические проверки ключевых требований учебного ТЗ."""
import os
import tempfile
import unittest
from datetime import datetime

from object_map import ObjectMap
from services.report_service import ReportService, WorkSession
from services.storage_service import StorageService


class ComplianceTests(unittest.TestCase):
    def test_custom_mapping(self):
        values = ObjectMap([("cars", 3), ("customers", 2)])
        self.assertEqual(values["cars"], 3)
        values["payments"] = 1
        self.assertEqual(len(values), 3)

    def test_work_session_special_methods_and_round_trip(self):
        session = WorkSession("admin", datetime(2026, 10, 9, 10, 0, 0), datetime(2026, 10, 9, 11, 0, 0))
        self.assertTrue(session.validate())
        self.assertIn("admin", str(session))
        self.assertIn("WorkSession", repr(session))
        restored = WorkSession.from_dict(session.to_dict())
        self.assertEqual(session, restored)

    def test_report_format_and_history(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "report.txt")
            report = ReportService(path)
            report.start_session("admin", datetime(2026, 10, 9, 10, 0, 0))
            report.finish_session(datetime(2026, 10, 9, 10, 15, 30))
            self.assertTrue(report.save_to_file())
            with open(path, encoding="utf-8") as stream:
                text = stream.read()
            self.assertIn("login", text)
            self.assertIn("time_in", text)
            self.assertIn("time_out", text)
            self.assertIn("09.10.2026 10:00:00", text)
            self.assertIn("09.10.2026 10:15:30", text)
            self.assertNotIn("rent_start", text)
            loaded = ReportService(path)
            self.assertEqual(loaded.session_count, 1)

    def test_json_compatibility_round_trip(self):
        source_path = os.path.join(os.path.dirname(__file__), "data.json")
        source = StorageService(source_path).load_all()
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "data.json")
            target = StorageService(path)
            self.assertTrue(target.save_all(source))
            restored = target.load_all()
            for name in target.COLLECTION_NAMES:
                self.assertEqual(restored[name].count, source[name].count, name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
