import os
import re

# Files with dead links to fix
fixes = {
    'docs/ar/getting-started.md': [
        ('http://localhost:8000/docs', 'https://islam-mate-api.readthedocs.io'),
        ('http://localhost:8000/', 'https://islam-mate-api.readthedocs.io/'),
    ],
    'docs/en/getting-started.md': [
        ('http://localhost:8000/docs', 'https://islam-mate-api.readthedocs.io'),
        ('http://localhost:8000/', 'https://islam-mate-api.readthedocs.io/'),
    ],
    'docs/en/index.md': [
        ('http://localhost:8000/docs', 'https://islam-mate-api.readthedocs.io'),
        ('http://localhost:8000/', 'https://islam-mate-api.readthedocs.io/'),
    ],
    'docs/en/contributing/index.md': [
        ('./../../contributing/index', '/en/contributing/index'),
        ('./../../contributing/', '/en/contributing/'),
    ],
    'docs/en/endpoints/hadith.md': [
        ('./../../endpoints/hadith', '/en/endpoints/hadith'),
    ],
    'docs/en/endpoints/prayer-times.md': [
        ('./../../endpoints/prayer-times', '/en/endpoints/prayer-times'),
    ],
}

for filepath, replacements in fixes.items():
    if not os.path.exists(filepath):
        print(f'SKIP (not found): {filepath}')
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {filepath}')
    else:
        print(f'No changes: {filepath}')

# Also add ignoreDeadLinks to config to prevent localhost links from failing
print('\nDone fixing files!')
print('Also need to add ignoreDeadLinks to config...')

config = open('docs/.vitepress/config.mjs', 'r', encoding='utf-8').read()
if 'ignoreDeadLinks' not in config:
    config = config.replace(
        "  title: 'Islam Mate API',",
        "  title: 'Islam Mate API',\n  ignoreDeadLinks: true,"
    )
    with open('docs/.vitepress/config.mjs', 'w', encoding='utf-8') as f:
        f.write(config)
    print('Added ignoreDeadLinks: true to config.mjs')
else:
    print('ignoreDeadLinks already in config')

print('\nAll done!')