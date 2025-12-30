
import PyInstaller.__main__
PyInstaller.__main__.run([
    'fix-helper.py',
    '--onefile',
    '--windowed',
    '--add-binary=UnRAR.exe;.',
    '--name=FixHelper',
    '--clean'
])