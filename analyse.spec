# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['analyse.py'],
             pathex=['D:\\Desktop\\labProject\\CnkiSpider'],
             binaries=[],
             datas=[('dataSrc','dataSrc'), ('./scrapy.cfg', '.'), ('./config.cfg', '.'), ('CnkiSpider/spiders', 'CnkiSpider/spiders'), ('log','log')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='analyse',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='cnki.ico')
