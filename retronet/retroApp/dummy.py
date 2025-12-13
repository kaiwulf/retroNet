NEWSGROUPS = [
    {
        'id': 1,
        'name': 'comp.lang.python',
        'description': 'Discussion about Python programming',
        'article_count': 142,
        'category': 'comp'
    },
    {
        'id': 2,
        'name': 'comp.retrocomputing',
        'description': 'Vintage computers and computing',
        'article_count': 89,
        'category': 'comp'
    },
    {
        'id': 3,
        'name': 'rec.games.retro',
        'description': 'Classic video games discussion',
        'article_count': 256,
        'category': 'rec'
    },
]

ARTICLES = [
    {
        'id': 1,
        'message_id': '<1234@retronet.local>',
        'newsgroup_id': 1,
        'subject': 'Welcome to retroNet!',
        'author': 'admin@retronet.local',
        'author_name': 'RetroNet Admin',
        'date': datetime(2025, 11, 1, 10, 30),
        'body': '''Welcome to retroNet - a classic Usenet experience!

This is a demonstration of how Usenet looked and felt in the 1990s.
Feel free to post messages, reply to threads, and explore the newsgroups.

Happy posting!

-- 
RetroNet Admin
retronet.local''',
        'parent_id': None,
        'read': False
    },
    {
        'id': 2,
        'message_id': '<1235@retronet.local>',
        'newsgroup_id': 1,
        'subject': 'Re: Welcome to retroNet!',
        'author': 'user@example.com',
        'author_name': 'John Doe',
        'date': datetime(2025, 11, 2, 14, 15),
        'body': '''On 11/1/2025, RetroNet Admin wrote:
> Welcome to retroNet - a classic Usenet experience!
> 
> This is a demonstration of how Usenet looked and felt in the 1990s.

This is great! Really captures that nostalgic feel.

Looking forward to seeing this develop.

-- 
John Doe
Vintage computing enthusiast''',
        'parent_id': 1,
        'read': False
    },
    {
        'id': 3,
        'message_id': '<1236@retronet.local>',
        'newsgroup_id': 2,
        'subject': 'Best vintage computer for hobbyist?',
        'author': 'retro@fan.net',
        'author_name': 'Retro Fan',
        'date': datetime(2025, 11, 3, 9, 45),
        'body': '''I\'m looking to get into vintage computing as a hobby.

What would you recommend for someone just starting out?
I\'m interested in programming and understanding how older
systems worked.

Thanks in advance!

-- 
Retro Fan''',
        'parent_id': None,
        'read': False
    },
]

