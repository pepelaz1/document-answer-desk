import unittest,tempfile,os
import engine
from unittest.mock import patch
import io,json
class Documents(unittest.TestCase):
    def setUp(self): engine.DB=os.path.join(os.getcwd(),'test-'+__import__('uuid').uuid4().hex+'.sqlite3')
    def tearDown(self): os.remove(engine.DB) if os.path.exists(engine.DB) else None
    def test_sources_and_missing_answer(self):
        r=engine.action('/api/ask',{'question':'How long do refunds take?'})
        self.assertEqual(r['sources'][0]['name'],'returns.md');self.assertIn('5 business days',r['answer'])
        self.assertEqual(len(r['sources']),1)
        self.assertEqual(engine.action('/api/ask',{'question':'quantum entanglement'})['sources'],[])
    def test_replace_document_and_plain_filenames(self):
        engine.action('/api/upload',{'name':'notes.txt','text':'Warranty lasts twelve months.'})
        engine.action('/api/upload',{'name':'notes.txt','text':'Warranty lasts six months.'})
        self.assertIn('six months',engine.action('/api/ask',{'question':'warranty'})['answer'])
        with self.assertRaises(ValueError): engine.action('/api/upload',{'name':'../notes.txt','text':'x'})
    def test_optional_generator_receives_sources(self):
        response=io.BytesIO(json.dumps({'message':{'content':'Refunds take 5 business days [1].'}}).encode())
        with patch.dict(os.environ,{'OLLAMA_MODEL':'test-model'}), patch('engine.urllib.request.urlopen',return_value=response) as transport:
            r=engine.action('/api/ask',{'question':'refunds'})
        self.assertEqual(r['mode'],'ollama')
        payload=json.loads(transport.call_args.args[0].data)
        self.assertFalse(payload['stream'])
        self.assertIn('[1]',payload['messages'][1]['content'])
