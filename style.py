config = open('docs/.vitepress/config.mjs', 'r', encoding='utf-8').read()

# Add dynamic base path for Read the Docs
old = "export default defineConfig({"
new = """export default defineConfig({
  base: process.env.READTHEDOCS_CANONICAL_URL
    ? new URL(process.env.READTHEDOCS_CANONICAL_URL).pathname
    : '/',"""

config = config.replace(old, new)

open('docs/.vitepress/config.mjs', 'w', encoding='utf-8').write(config)
print('Done! Base path set dynamically for Read the Docs')
print('On RTD it will be: /en/latest/')
print('Locally it will be: /')