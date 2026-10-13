"""Regression checks for automatic repository cards; no network access."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
import xml.etree.ElementTree as ET

import refresh_profile as profile


def repo(number, name, **changes):
    value = dict(id=number, name=name, fork=False, private=False,
                 created_at=f'2026-10-{number:02d}T00:00:00Z',
                 description='中文描述 <tag> & "quotes" ' * 20,
                 language=None, stargazers_count=0,
                 html_url=f'https://github.com/Rocdna/{name}')
    value.update(changes)
    return value


class ProjectCardsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(profile, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.readme = self.root / 'README.md'
        self.readme.write_text('介绍\n<!-- PROJECTS:START -->\nold\n'
                               '<!-- PROJECTS:END -->\n其他内容', encoding='utf-8')

    def test_new_repository_added_first_and_old_repository_removed(self):
        profile.project_cards([repo(1, 'old')])
        profile.project_cards([repo(1, 'old'), repo(2, 'new')])
        source = self.readme.read_text(encoding='utf-8')
        self.assertLess(source.index('repo-2.svg'), source.index('repo-1.svg'))
        self.assertTrue(source.startswith('介绍\n'))
        self.assertTrue(source.endswith('\n其他内容'))
        profile.project_cards([repo(2, 'renamed')])
        self.assertFalse((self.root / 'assets/projects/repo-1.svg').exists())
        self.assertIn('/renamed', self.readme.read_text(encoding='utf-8'))
        ET.parse(self.root / 'assets/projects/repo-2.svg')

    def test_private_forks_and_profile_excluded_and_empty_state(self):
        profile.project_cards([repo(1, 'public')])
        profile.project_cards([repo(1, 'public', private=True),
                               repo(2, 'fork', fork=True), repo(3, 'ROCDNA')])
        self.assertIn('暂无公开原创项目', self.readme.read_text(encoding='utf-8'))
        self.assertEqual(list((self.root / 'assets/projects').glob('repo-*.svg')), [])

    def test_long_unicode_description_and_invalid_markers(self):
        profile.project_cards([repo(1, '长名称' * 20)])
        tree = ET.parse(self.root / 'assets/projects/repo-1.svg')
        texts = tree.findall('.//{http://www.w3.org/2000/svg}text')
        self.assertTrue(any('…' in node.text for node in texts))
        previous = self.readme.read_text(encoding='utf-8').replace('PROJECTS:END', 'BROKEN')
        self.readme.write_text(previous, encoding='utf-8')
        with self.assertRaises(RuntimeError):
            profile.project_cards([])
        self.assertEqual(self.readme.read_text(encoding='utf-8'), previous)
        self.assertTrue((self.root / 'assets/projects/repo-1.svg').exists())


if __name__ == '__main__':
    unittest.main()
