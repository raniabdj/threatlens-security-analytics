import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pipeline

class PipelineTests(unittest.TestCase):
    def test_determinism_and_scenarios(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(pipeline,'DATA',Path(d)/'data'), patch.object(pipeline,'OUTPUTS',Path(d)/'out'):
                self.assertEqual(pipeline.generate(),1223)
                first=(pipeline.DATA/'events.csv').read_bytes()
                pipeline.generate()
                self.assertEqual(first,(pipeline.DATA/'events.csv').read_bytes())
                conn=pipeline.load()
                result=pipeline.analyze(conn)
                self.assertTrue(any(r['user_id']=='employee07' and r['src_ip']=='198.51.100.77' for r in result['01_failed_login_bursts']))
                self.assertTrue(any(r['user_id']=='employee07' for r in result['02_success_after_failures']))
                self.assertTrue(any(r['destination_ip']=='203.0.113.250' for r in result['03_destination_outliers']))
                self.assertEqual(result['summary']['total_events'],1223)
                conn.close()

if __name__=='__main__': unittest.main()
