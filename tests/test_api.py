import json
import threading
import unittest
from http.server import HTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError

from app.main import Handler


class CloudForgeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health_endpoint(self):
        with urlopen(
            f"http://127.0.0.1:{self.port}/health"
        ) as response:
            data = json.loads(response.read())

            self.assertEqual(response.status, 200)
            self.assertEqual(data["status"], "healthy")

    def test_ready_endpoint(self):
        with urlopen(
            f"http://127.0.0.1:{self.port}/ready"
        ) as response:
            data = json.loads(response.read())

            self.assertEqual(response.status, 200)
            self.assertEqual(data["path"], "/ready")

    def test_unknown_endpoint(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(
                f"http://127.0.0.1:{self.port}/unknown"
            )

        self.assertEqual(error.exception.code, 404)
        error.exception.close()


if __name__ == "__main__":
    unittest.main()
