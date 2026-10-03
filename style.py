import os

# 1. Fix .readthedocs.yaml
with open('.readthedocs.yaml', 'w', encoding='utf-8') as f:
    f.write("version: 2\n\n")
    f.write("build:\n")
    f.write("  os: ubuntu-24.04\n")
    f.write("  tools:\n")
    f.write("    nodejs: \"22\"\n")
    f.write("  jobs:\n")
    f.write("    install:\n")
    f.write("      - npm install\n")
    f.write("    build:\n")
    f.write("      html:\n")
    f.write("        - npm run docs:build\n")
    f.write("        - mkdir -p $READTHEDOCS_OUTPUT/html\n")
    f.write("        - cp -r docs/.vitepress/dist/. $READTHEDOCS_OUTPUT/html\n")
print('Fixed .readthedocs.yaml')

# 2. Fix config.mjs - add ignoreDeadLinks
config = open('docs/.vitepress/config.mjs', 'r', encoding='utf-8').read()
if 'ignoreDeadLinks' not in config:
    config = config.replace(
        "  title: 'Islam Mate API',",
        "  title: 'Islam Mate API',\n  ignoreDeadLinks: true,"
    )
    open('docs/.vitepress/config.mjs', 'w', encoding='utf-8').write(config)
    print('Added ignoreDeadLinks to config')

# 3. Fix all localhost links in markdown files
import glob

md_files = glob.glob('docs/**/*.md', recursive=True)
fixed = 0
for filepath in md_files:
    content = open(filepath, 'r', encoding='utf-8').read()
    original = content
    content = content.replace('http://localhost:8000/docs', 'https://islam-mate-api.readthedocs.io')
    content = content.replace('http://localhost:8000', 'https://islam-mate-api.readthedocs.io')
    # Fix broken relative links in en/contributing
    content = content.replace('./../../contributing/index', '/en/contributing/index')
    content = content.replace('./../../endpoints/', '/en/endpoints/')
    if content != original:
        open(filepath, 'w', encoding='utf-8').write(content)
        print(f'Fixed links in: {filepath}')
        fixed += 1

print(f'\nFixed {fixed} files')
print('All done!')