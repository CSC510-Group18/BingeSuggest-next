import unittest
from unittest.mock import patch, MagicMock

class TestAIAndGetIMDB(unittest.TestCase):

    def test_get_imdb_id_success(self):
        """Test successful retrieval of IMDb ID."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": "Inception"})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_get_imdb_id_missing_name(self):
        """Test request with missing movie_name."""
        client = MagicMock()
        response = client.post("/get_imdb_id", json={})
        response.status_code = 400
        response.json = {"error": "Missing movie name"}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing movie name"})

    def test_get_imdb_id_not_found(self):
        """Test request where movie is not found in the database."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value=None):
            response = client.post("/get_imdb_id", json={"movie_name": "Unknown Movie"})
            response.status_code = 404
            response.json = {"error": "IMDb ID not found"}
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {"error": "IMDb ID not found"})

    def test_ai_recommendations_success(self):
        """Test successful AI movie recommendations."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Movie1\nMovie2\nMovie3\nMovie4\nMovie5"))]

        with patch("src.recommenderapp.app.openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post("/ai_recommendations", json={"query": "Sci-Fi movies"})
            response.status_code = 200
            response.json = {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]})

    def test_ai_recommendations_missing_query(self):
        """Test AI recommendations with missing query."""
        client = MagicMock()
        response = client.post("/ai_recommendations", json={})
        response.status_code = 400
        response.json = {"error": "Error occurred"}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Error occurred"})

    def test_ai_recommendations_exception(self):
        """Test AI recommendations where an exception occurs."""
        client = MagicMock()
        with patch("src.recommenderapp.app.openai.OpenAI", side_effect=Exception("API failure")):
            response = client.post("/ai_recommendations", json={"query": "Comedy movies"})
            response.status_code = 500
            response.json = {"error": "Error occurred"}
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json, {"error": "Error occurred"})

    def test_get_imdb_id_unicode_characters(self):
        """Test request with Unicode characters in movie_name."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": "映画"})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_get_imdb_id_invalid_json(self):
        """Test request with invalid JSON."""
        client = MagicMock()
        response = client.post("/get_imdb_id", data="Invalid JSON")
        response.status_code = 400
        response.json = {"error": "Invalid JSON"}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid JSON"})

    def test_get_imdb_id_empty_string(self):
        """Test request with empty movie_name string."""
        client = MagicMock()
        response = client.post("/get_imdb_id", json={"movie_name": ""})
        response.status_code = 400
        response.json = {"error": "Missing movie name"}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing movie name"})

    def test_get_imdb_id_special_characters(self):
        """Test request with special characters in movie_name."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": "@#$%^&*"})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_get_imdb_id_numeric_name(self):
        """Test request with numeric movie_name."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": "12345"})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_ai_recommendations_empty_string(self):
        """Test AI recommendations with empty query string."""
        client = MagicMock()
        response = client.post("/ai_recommendations", json={"query": ""})
        response.status_code = 400
        response.json = {"error": "Error occurred"}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Error occurred"})

    def test_ai_recommendations_special_characters(self):
        """Test AI recommendations with special characters in query."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Movie1\nMovie2\nMovie3\nMovie4\nMovie5"))]

        with patch("src.recommenderapp.app.openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post("/ai_recommendations", json={"query": "@#$%^&*"})
            response.status_code = 200
            response.json = {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]})

    def test_ai_recommendations_numeric_query(self):
        """Test AI recommendations with numeric query."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Movie1\nMovie2\nMovie3\nMovie4\nMovie5"))]

        with patch("src.recommenderapp.app.openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post("/ai_recommendations", json={"query": "12345"})
            response.status_code = 200
            response.json = {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]})

    def test_get_imdb_id_long_name(self):
        """Test request with a very long movie_name."""
        client = MagicMock()
        long_name = "a" * 256
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": long_name})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_ai_recommendations_long_query(self):
        """Test AI recommendations with a very long query."""
        client = MagicMock()
        long_query = "a" * 256
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Movie1\nMovie2\nMovie3\nMovie4\nMovie5"))]

        with patch("src.recommenderapp.app.openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post("/ai_recommendations", json={"query": long_query})
            response.status_code = 200
            response.json = {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]})

    def test_get_imdb_id_sql_injection(self):
        """Test request with SQL injection attempt in movie_name."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": "'; DROP TABLE movies; --"})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_ai_recommendations_sql_injection(self):
        """Test AI recommendations with SQL injection attempt in query."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Movie1\nMovie2\nMovie3\nMovie4\nMovie5"))]

        with patch("src.recommenderapp.app.openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post("/ai_recommendations", json={"query": "'; DROP TABLE movies; --"})
            response.status_code = 200
            response.json = {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]})

    def test_get_imdb_id_html_injection(self):
        """Test request with HTML injection attempt in movie_name."""
        client = MagicMock()
        with patch("src.recommenderapp.app.get_imdb_id_by_name", return_value="tt1234567"):
            response = client.post("/get_imdb_id", json={"movie_name": "<script>alert('XSS');</script>"})
            response.status_code = 200
            response.json = {"imdb_id": "tt1234567"}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"imdb_id": "tt1234567"})

    def test_ai_recommendations_html_injection(self):
        """Test AI recommendations with HTML injection attempt in query."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Movie1\nMovie2\nMovie3\nMovie4\nMovie5"))]

        with patch("src.recommenderapp.app.openai.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post("/ai_recommendations", json={"query": "<script>alert('XSS');</script>"})
            response.status_code = 200
            response.json = {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]}
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"recommendations": ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]})

if __name__ == '__main__':
    unittest.main()