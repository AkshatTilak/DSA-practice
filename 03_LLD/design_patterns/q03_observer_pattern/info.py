INFO = {
    'difficulty': 'Medium',
    'link': 'https://refactoring.guru/design-patterns/observer',
    'description': 'Implement Publish-Subscribe dynamic messaging engine via Observer Pattern.',
    'groups': ['Behavioral Patterns'],
    'starter_code': 'class Subject:\n    def __init__(self):\n        self._observers = []\n    def register(self, obs):\n        self._observers.append(obs)\n    def notify(self, event: str):\n        for o in self._observers: o.update(event)\n\nclass Observer:\n    def update(self, event: str):\n        pass',
    'solutions': '# Observer implementations',
    'test_code': 'def test_observer():\n    pass',
    'readme_content': '# Observer Pattern\nDecoupled event bindings.',
}
