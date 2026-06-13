INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.systemdesignprimer.com/consistent-hashing',
    'description': 'Implement consistent hashing ring with virtual nodes configuration.',
    'groups': ['Distributed Systems', 'Hashing'],
    'starter_code': 'import hashlib\n\nclass ConsistentHashRing:\n    def __init__(self, replicas=3):\n        self.replicas = replicas\n        self.ring = {} # hash -> node\n        self.sorted_keys = []\n\n    def add_node(self, node: str) -> None:\n        pass\n    def remove_node(self, node: str) -> None:\n        pass\n    def get_node(self, key: str) -> str:\n        pass',
    'solutions': '# Consistent hashing allocations',
    'test_code': 'def test_hashing():\n    pass',
    'readme_content': '# Consistent Hashing\nNode rings virtual configurations.',
}
