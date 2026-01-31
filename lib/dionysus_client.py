"""
Dionysus Memory Client

Provides integration between Archimedes and the Dionysus VPS
for storing and retrieving memories via Graphiti knowledge graph.

Usage:
    from lib.dionysus_client import DionysusClient
    
    client = DionysusClient()
    
    # Store a memory
    result = client.store_memory(
        content="Important insight about the project",
        source="archimedes",
        metadata={"category": "project", "importance": "high"}
    )
    
    # Search memories
    memories = client.search_memories("project insights", limit=10)
    
    # Check health
    health = client.health_check()
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Any


class DionysusClient:
    """Client for Dionysus memory API."""
    
    DEFAULT_BASE_URL = "http://72.61.78.89:8000"
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the Dionysus client.
        
        Args:
            base_url: Base URL for the Dionysus API (default: http://72.61.78.89:8000)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
    
    def _request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Optional JSON data to send
            
        Returns:
            Parsed JSON response
            
        Raises:
            DionysusError: On API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        request = urllib.request.Request(url, method=method)
        request.add_header("Content-Type", "application/json")
        
        body = None
        if data:
            body = json.dumps(data).encode("utf-8")
        
        try:
            with urllib.request.urlopen(request, body, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            raise DionysusError(f"HTTP {e.code}: {error_body}") from e
        except urllib.error.URLError as e:
            raise DionysusError(f"Connection error: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise DionysusError(f"Invalid JSON response: {e}") from e
    
    def health_check(self) -> dict:
        """
        Check if the Dionysus API is healthy.
        
        Returns:
            Health status dict with 'status', 'service', and 'meta_tot_thresholds'
            
        Example:
            >>> client.health_check()
            {'status': 'healthy', 'service': 'dionysus-core', ...}
        """
        return self._request("GET", "/health")
    
    def store_memory(
        self,
        content: str,
        source: str = "archimedes",
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Store a memory in the Dionysus knowledge graph.
        
        Args:
            content: The memory content/text to store
            source: Source identifier (default: "archimedes")
            metadata: Optional additional metadata dict
            
        Returns:
            Response with 'episode_uuid', 'nodes', and 'edges' created
            
        Example:
            >>> client.store_memory(
            ...     content="User prefers morning meetings",
            ...     source="archimedes",
            ...     metadata={"category": "preference"}
            ... )
            {'episode_uuid': '...', 'nodes': [...], 'edges': [...]}
        """
        payload = {
            "content": content,
            "source": source,
        }
        if metadata:
            payload["metadata"] = metadata
        
        return self._request("POST", "/api/graphiti/ingest", payload)
    
    def search_memories(self, query: str, limit: int = 10) -> dict:
        """
        Search for memories in the knowledge graph.
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 10)
            
        Returns:
            Response with 'edges' list and 'count'
            
        Example:
            >>> client.search_memories("project deadlines", limit=5)
            {'edges': [...], 'count': 5}
        """
        payload = {
            "query": query,
            "limit": limit,
        }
        return self._request("POST", "/api/graphiti/search", payload)
    
    def is_available(self) -> bool:
        """
        Quick check if the API is reachable.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            result = self.health_check()
            return result.get("status") == "healthy"
        except DionysusError:
            return False


class DionysusError(Exception):
    """Exception raised for Dionysus API errors."""
    pass


# Convenience functions for quick access
_default_client: Optional[DionysusClient] = None


def get_client() -> DionysusClient:
    """Get or create the default client instance."""
    global _default_client
    if _default_client is None:
        _default_client = DionysusClient()
    return _default_client


def store_memory(content: str, source: str = "archimedes", metadata: Optional[dict] = None) -> dict:
    """Convenience function to store a memory using the default client."""
    return get_client().store_memory(content, source, metadata)


def search_memories(query: str, limit: int = 10) -> dict:
    """Convenience function to search memories using the default client."""
    return get_client().search_memories(query, limit)


def health_check() -> dict:
    """Convenience function to check health using the default client."""
    return get_client().health_check()


if __name__ == "__main__":
    # Quick test when run directly
    client = DionysusClient()
    
    print("Testing Dionysus connection...")
    print(f"Health: {client.health_check()}")
    
    print("\nStoring test memory...")
    result = client.store_memory(
        content="Test memory from dionysus_client.py",
        source="archimedes-test"
    )
    print(f"Stored: episode_uuid={result.get('episode_uuid')}")
    
    print("\nSearching memories...")
    results = client.search_memories("test", limit=3)
    print(f"Found {results.get('count', 0)} results")
