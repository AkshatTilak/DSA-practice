INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/reverse-linked-list/',
    'description': 'Reverse a singly linked list.',
    'groups': ['Linked List'],
    'starter_code': 'class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head: ListNode) -> ListNode:\n    # Write your solution here\n    pass',
    'solutions': '# Iterative pointer swapping O(N)\ndef reverse_list_optimal(head):\n    prev, curr = None, head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev',
    'test_code': 'def test_reverse():\n    # Setup simple list 1->2 and reverse\n    pass',
    'readme_content': '# Reverse Linked List\nSwapping pointers sequentially.',
}
