#!/usr/bin/env python3
"""
SM Tool — Unified Spider-Man Asset Tool (GUI + CLI)
Supports all 5 games: SM1 PS4, MM PS4, SM Remastered PS5/PC, MM PS5/PC, SM2 PS5
"""

import sys, os, argparse, io, traceback

# ─── Theme ──────────────────────────────────────────────────────────────────────
THEME = {
    'bg':           '#0D0D0D',
    'panel':        '#1A1A2E',
    'panel_light':  '#252545',
    'red':          '#E23636',
    'red_dark':     '#B1131B',
    'blue':         '#2B5F8E',
    'blue_light':   '#3A7FBF',
    'text':         '#FFFFFF',
    'text_dim':     '#B0B0B0',
    'green':        '#4CAF50',
    'orange':       '#FF9800',
    'input_bg':     '#12122A',
    'input_fg':     '#FFFFFF',
    'border':       '#333355',
}

# ─── Game Registry ──────────────────────────────────────────────────────────────
GAMES = {
    'sm1': {
        'name': "Marvel's Spider-Man - PS4",
        'module': 'sm1',
        'hashdb': 'PS4AssetHashes.txt',
        'stride': 24,
        'font_hash': '0xB1BC4746124FA7ED',
        'loc_hash': '0xBE55D94F171BF8DE',
        'font_format': 'GFX',
        'strings': '54,010',
        'wip': False,
    },
    'mm': {
        'name': "Marvel's Spider-Man: Miles Morales - PS4",
        'module': 'mm',
        'hashdb': 'MilesAssetHashes.txt',
        'stride': 72,
        'font_hash': '0xB1BC4746124FA7ED',
        'loc_hash': '0xBE55D94F171BF8DE',
        'font_format': 'GFX',
        'strings': '34,079',
        'wip': False,
    },
    'smr': {
        'name': "Marvel's Spider-Man Remastered - PS5/PC",
        'module': 'smr',
        'hashdb': 'PS5AssetHashes.txt',
        'stride': 72,
        'font_hash': '0xB1BC4746124FA7ED',
        'loc_hash': '0xBE55D94F171BF8DE',
        'font_format': 'GFX',
        'strings': '56,417',
        'wip': False,
    },
    'mm_ps5': {
        'name': "Marvel's Spider-Man: Miles Morales - PS5/PC",
        'module': 'smr',
        'hashdb': 'PS5AssetHashes.txt',
        'stride': 72,
        'font_hash': '0xB1BC4746124FA7ED',
        'loc_hash': '0xBE55D94F171BF8DE',
        'font_format': 'GFX',
        'strings': '34,076',
        'wip': False,
    },
    'sm2': {
        'name': "Marvel's Spider-Man 2 - PS5",
        'module': 'sm2',
        'hashdb': 'hashes.txt',
        'stride': 66,
        'font_hash': '0x8143F7F3648B4470',
        'loc_hash': '0xBE55D94F171BF8DE',
        'font_format': 'TTF/OTF',
        'strings': '92,760',
        'wip': True,
    },
}


# ─── Backend Runner ─────────────────────────────────────────────────────────────
class Backend:
    """Run backend tool commands and capture output."""
    @staticmethod
    def run(game_id, argv):
        """Execute a backend command. Returns (success, output)."""
        game = GAMES[game_id]
        mod_name = game['module']

        # Import the right module
        if mod_name == 'sm1':
            from sm1 import main as sm1_main
            target = sm1_main
        elif mod_name == 'mm':
            from mm import main as mm_main
            target = mm_main
        elif mod_name == 'smr':
            from smr import main as smr_main
            target = smr_main
        elif mod_name == 'sm2':
            from sm2 import main as sm2_main
            target = sm2_main
        else:
            return False, f"Unknown module: {mod_name}"

        # Capture stdout
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = sys.stdout
        old_argv = sys.argv

        try:
            sys.argv = [mod_name] + argv
            target()
            output = sys.stdout.getvalue()
            return True, output
        except SystemExit:
            output = sys.stdout.getvalue()
            return 'error' not in output.lower(), output
        except Exception as e:
            output = sys.stdout.getvalue()
            output += f'\n[ERROR] {e}\n{traceback.format_exc()}'
            return False, output
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.argv = old_argv

    @staticmethod
    def run_loc_export(game_id, loc_path, csv_path):
        game = GAMES[game_id]
        mod_name = game['module']
        if mod_name == 'sm1':
            from sm1 import loc_export
        elif mod_name == 'mm':
            from sm1 import loc_export
        elif mod_name == 'smr':
            from smr import loc_export
        elif mod_name == 'sm2':
            from sm2 import loc_export
        else:
            return False, f"Unknown module: {mod_name}"

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            count = loc_export(loc_path, csv_path)
            output = sys.stdout.getvalue()
            return True, output
        except Exception as e:
            output = sys.stdout.getvalue() + f'\n[ERROR] {e}'
            return False, output
        finally:
            sys.stdout = old_stdout

    @staticmethod
    def run_loc_import(game_id, loc_path, csv_path, out_path):
        game = GAMES[game_id]
        mod_name = game['module']
        if mod_name == 'sm1':
            from sm1 import loc_import
        elif mod_name == 'mm':
            from sm1 import loc_import
        elif mod_name == 'smr':
            from smr import loc_import
        elif mod_name == 'sm2':
            from sm2 import loc_import
        else:
            return False, f"Unknown module: {mod_name}"

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            count = loc_import(loc_path, csv_path, out_path)
            output = sys.stdout.getvalue()
            return True, output
        except Exception as e:
            output = sys.stdout.getvalue() + f'\n[ERROR] {e}'
            return False, output
        finally:
            sys.stdout = old_stdout


# ─── GUI ────────────────────────────────────────────────────────────────────────
class SpiderToolGUI:
    def __init__(self):
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox, scrolledtext

        self.tk = tk
        self.ttk = ttk
        self.filedialog = filedialog
        self.messagebox = messagebox
        self.scrolledtext = scrolledtext

        self.root = tk.Tk()
        self.root.title("🕷️ Spider-Man Asset Tool")
        self.root.geometry("820x720")
        self.root.configure(bg=THEME['bg'])
        self.root.resizable(True, True)
        self.root.minsize(700, 600)

        # Try to set icon
        try:
            self.root.iconbitmap(default='')
        except:
            pass

        self.current_game = tk.StringVar(value='smr')
        self.toc_path = tk.StringVar()
        self.archive_dir = tk.StringVar()
        self.asset_index = tk.StringVar(value='0')
        self.slot_index = tk.StringVar(value='1')

        self._build_ui()
        self._on_game_change()  # init defaults

    def _build_ui(self):
        t = THEME
        tk = self.tk
        ttk = self.ttk

        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=t['bg'])
        style.configure('TLabelframe', background=t['bg'], foreground=t['text'], bordercolor=t['border'])
        style.configure('TLabelframe.Label', background=t['bg'], foreground=t['red'], font=('Segoe UI', 10, 'bold'))
        style.configure('TRadiobutton', background=t['panel'], foreground=t['text'], font=('Segoe UI', 10))
        style.map('TRadiobutton', background=[('active', t['panel_light'])])
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.configure('Red.TButton', background=t['red'], foreground='white')
        style.configure('TEntry', fieldbackground=t['input_bg'], foreground=t['input_fg'])

        # ─── Title ───
        title_frame = tk.Frame(self.root, bg=t['red_dark'], height=50)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title = tk.Label(title_frame, text="🕷️  SPIDER-MAN ASSET TOOL",
                        font=('Segoe UI', 18, 'bold'), bg=t['red_dark'], fg=t['text'])
        title.pack(side='left', padx=15, pady=8)

        version = tk.Label(title_frame, text="v3.0", font=('Segoe UI', 9),
                          bg=t['red_dark'], fg=t['text_dim'])
        version.pack(side='right', padx=15, pady=8)

        # ─── Main content ───
        main = tk.Frame(self.root, bg=t['bg'])
        main.pack(fill='both', expand=True, padx=10, pady=8)

        # Left panel — game selection
        left = tk.Frame(main, bg=t['bg'])
        left.pack(side='left', fill='y', padx=(0, 8))

        # ─── Game Selection ───
        game_frame = tk.LabelFrame(left, text=" GAME SELECTION ", bg=t['bg'],
                                   fg=t['red'], font=('Segoe UI', 11, 'bold'),
                                   padx=10, pady=8)
        game_frame.pack(fill='x')

        self.game_radios = {}
        game_order = ['sm1', 'mm', 'smr', 'mm_ps5', 'sm2']
        for gid in game_order:
            g = GAMES[gid]
            label = g['name']
            if g['wip']:
                label += '  🚧 WIP'

            frame = tk.Frame(game_frame, bg=t['panel'], height=30)
            frame.pack(fill='x', pady=2)
            frame.pack_propagate(False)

            rb = tk.Radiobutton(frame, text=label, variable=self.current_game, value=gid,
                               bg=t['panel'], fg=t['text'], font=('Segoe UI', 10),
                               activebackground=t['panel_light'], activeforeground=t['red'],
                               selectcolor=t['panel'], command=self._on_game_change,
                               anchor='w', padx=8)
            rb.pack(fill='both', expand=True)

            if g['wip']:
                warn = tk.Label(frame, text='⚠', bg=t['panel'], fg=t['orange'], font=('Segoe UI', 10))
                warn.pack(side='right', padx=5)

            self.game_radios[gid] = rb

        # Game info
        self.info_text = tk.StringVar()
        info_label = tk.Label(left, textvariable=self.info_text, bg=t['bg'],
                             fg=t['text_dim'], font=('Segoe UI', 8), justify='left')
        info_label.pack(fill='x', pady=(5, 0))

        # ─── Right panel — settings + actions ───
        right = tk.Frame(main, bg=t['bg'])
        right.pack(side='left', fill='both', expand=True)

        # Settings
        settings = tk.LabelFrame(right, text=" SETTINGS ", bg=t['bg'],
                                fg=t['red'], font=('Segoe UI', 11, 'bold'),
                                padx=10, pady=8)
        settings.pack(fill='x', pady=(0, 8))

        # TOC path
        tk.Label(settings, text='TOC File:', bg=t['bg'], fg=t['text'],
                font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w', pady=3)
        toc_entry = tk.Entry(settings, textvariable=self.toc_path, width=45,
                            bg=t['input_bg'], fg=t['input_fg'], insertbackground=t['text'])
        toc_entry.grid(row=0, column=1, padx=5, pady=3)
        tk.Button(settings, text='Browse', command=self._browse_toc,
                 bg=t['blue'], fg=t['text'], font=('Segoe UI', 8),
                 relief='flat', padx=8).grid(row=0, column=2, pady=3)

        # Archive dir
        tk.Label(settings, text='Archive Dir:', bg=t['bg'], fg=t['text'],
                font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=3)
        tk.Entry(settings, textvariable=self.archive_dir, width=45,
                bg=t['input_bg'], fg=t['input_fg'], insertbackground=t['text']).grid(row=1, column=1, padx=5, pady=3)
        tk.Button(settings, text='Browse', command=self._browse_archive,
                 bg=t['blue'], fg=t['text'], font=('Segoe UI', 8),
                 relief='flat', padx=8).grid(row=1, column=2, pady=3)

        # Options row
        opts = tk.Frame(settings, bg=t['bg'])
        opts.grid(row=2, column=0, columnspan=3, sticky='w', pady=5)

        tk.Label(opts, text='Asset Index:', bg=t['bg'], fg=t['text_dim'],
                font=('Segoe UI', 8)).pack(side='left')
        tk.Entry(opts, textvariable=self.asset_index, width=4,
                bg=t['input_bg'], fg=t['input_fg']).pack(side='left', padx=(2, 12))

        tk.Label(opts, text='Slot (--asset-index):', bg=t['bg'], fg=t['text_dim'],
                font=('Segoe UI', 8)).pack(side='left')
        tk.Entry(opts, textvariable=self.slot_index, width=4,
                bg=t['input_bg'], fg=t['input_fg']).pack(side='left', padx=(2, 12))

        self.hashdb_label = tk.Label(opts, text='', bg=t['bg'], fg=t['text_dim'],
                                     font=('Segoe UI', 8))
        self.hashdb_label.pack(side='left')

        # ─── Actions ───
        actions = tk.LabelFrame(right, text=" ACTIONS ", bg=t['bg'],
                               fg=t['red'], font=('Segoe UI', 11, 'bold'),
                               padx=10, pady=8)
        actions.pack(fill='x', pady=(0, 8))

        btn_config = {'font': ('Segoe UI', 9), 'relief': 'flat', 'padx': 10, 'pady': 4, 'width': 16}

        row1 = tk.Frame(actions, bg=t['bg'])
        row1.pack(fill='x', pady=2)
        row2 = tk.Frame(actions, bg=t['bg'])
        row2.pack(fill='x', pady=2)
        row3 = tk.Frame(actions, bg=t['bg'])
        row3.pack(fill='x', pady=2)

        self.btn_extract_loc = tk.Button(row1, text='📦 Extract Loc', bg=t['blue'], fg=t['text'],
                                        command=self._extract_loc, **btn_config)
        self.btn_extract_loc.pack(side='left', padx=3)

        self.btn_extract_font = tk.Button(row1, text='🔤 Extract Font', bg=t['blue'], fg=t['text'],
                                         command=self._extract_font, **btn_config)
        self.btn_extract_font.pack(side='left', padx=3)

        self.btn_export = tk.Button(row1, text='📝 Export CSV', bg=t['blue'], fg=t['text'],
                                   command=self._export_csv, **btn_config)
        self.btn_export.pack(side='left', padx=3)

        self.btn_import = tk.Button(row2, text='📥 Import CSV', bg=t['orange'], fg='#000',
                                   command=self._import_csv, **btn_config)
        self.btn_import.pack(side='left', padx=3)

        self.btn_patch_loc = tk.Button(row2, text='💾 Patch Loc', bg=t['orange'], fg='#000',
                                      command=self._patch_loc, **btn_config)
        self.btn_patch_loc.pack(side='left', padx=3)

        self.btn_patch_both = tk.Button(row2, text='💾 Patch Loc+Font', bg=t['red'], fg=t['text'],
                                       command=self._patch_both, **btn_config)
        self.btn_patch_both.pack(side='left', padx=3)

        self.btn_info = tk.Button(row3, text='ℹ️ TOC Info', bg=t['panel_light'], fg=t['text'],
                                  command=self._toc_info, **btn_config)
        self.btn_info.pack(side='left', padx=3)

        # WIP warning
        self.wip_label = tk.Label(actions, text='', bg=t['bg'], fg=t['orange'],
                                  font=('Segoe UI', 9, 'italic'))
        self.wip_label.pack(fill='x', pady=(5, 0))

        # ─── Log ───
        log_frame = tk.LabelFrame(right, text=" LOG ", bg=t['bg'],
                                 fg=t['red'], font=('Segoe UI', 11, 'bold'),
                                 padx=10, pady=8)
        log_frame.pack(fill='both', expand=True)

        self.log = self.scrolledtext.ScrolledText(log_frame, height=10, wrap='word',
                                                   bg='#0A0A15', fg=t['text'],
                                                   font=('Consolas', 9),
                                                   insertbackground=t['text'])
        self.log.pack(fill='both', expand=True)
        self.log.config(state='disabled')

        # ─── Status bar ───
        status = tk.Frame(self.root, bg=t['panel'], height=22)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)

        self.status_text = tk.StringVar(value='🕸️ Ready')
        tk.Label(status, textvariable=self.status_text, bg=t['panel'], fg=t['text_dim'],
                font=('Segoe UI', 8)).pack(side='left', padx=10)

    def _on_game_change(self, *args):
        gid = self.current_game.get()
        g = GAMES[gid]
        self.info_text.set(f"Hash DB: {g['hashdb']}\nStride: {g['stride']}  |  "
                          f"Strings: {g['strings']}\nFont: {g['font_hash']} ({g['font_format']})")
        self.hashdb_label.config(text=f"HashDB: {g['hashdb']}")

        if g['wip']:
            self.wip_label.config(text='🚧 SM2 is WIP — Extract + Export only')
            self.btn_import.config(state='disabled', bg='#555')
            self.btn_patch_loc.config(state='disabled', bg='#555')
            self.btn_patch_both.config(state='disabled', bg='#555')
        else:
            self.wip_label.config(text='')
            self.btn_import.config(state='normal', bg=THEME['orange'])
            self.btn_patch_loc.config(state='normal', bg=THEME['orange'])
            self.btn_patch_both.config(state='normal', bg=THEME['red'])

    def _browse_toc(self):
        path = self.filedialog.askopenfilename(title='Select TOC file', filetypes=[('TOC', 'toc'), ('All', '*.*')])
        if path:
            self.toc_path.set(path)
            # Auto-detect archive dir
            parent = os.path.dirname(path)
            if os.path.isdir(os.path.join(parent, 'd')):
                self.archive_dir.set(parent)

    def _browse_archive(self):
        path = self.filedialog.askdirectory(title='Select Archive Directory')
        if path:
            self.archive_dir.set(path)

    def _log(self, text):
        self.log.config(state='normal')
        self.log.insert('end', text + '\n')
        self.log.see('end')
        self.log.config(state='normal')
        self.root.update()

    def _run_cmd(self, argv, desc=''):
        if desc:
            self._log(f'\n--- {desc} ---')
        gid = self.current_game.get()
        success, output = Backend.run(gid, argv)
        self._log(output)
        if success:
            self.status_text.set(f'✅ {desc} completed')
        else:
            self.status_text.set(f'❌ {desc} failed')
        return success

    def _ensure_paths(self):
        if not self.toc_path.get():
            self.messagebox.showerror('Error', 'Select TOC file first')
            return False
        if not self.archive_dir.get():
            self.messagebox.showerror('Error', 'Select Archive Directory first')
            return False
        return True

    def _extract_loc(self):
        if not self._ensure_paths(): return
        g = GAMES[self.current_game.get()]
        out = self.filedialog.askdirectory(title='Output directory')
        if not out: return
        self._run_cmd([
            '--toc', self.toc_path.get(),
            '--hashdb', g['hashdb'],
            'extract',
            '--archive-dir', self.archive_dir.get(),
            '--id', g['loc_hash'],
            '--output', out,
            '--flat',
        ], f'Extract Loc ({g["name"]})')

    def _extract_font(self):
        if not self._ensure_paths(): return
        g = GAMES[self.current_game.get()]
        out = self.filedialog.askdirectory(title='Output directory')
        if not out: return
        self._run_cmd([
            '--toc', self.toc_path.get(),
            '--hashdb', g['hashdb'],
            'extract',
            '--archive-dir', self.archive_dir.get(),
            '--id', g['font_hash'],
            '--output', out,
        ], f'Extract Font ({g["name"]})')

    def _export_csv(self):
        g = GAMES[self.current_game.get()]
        loc = self.filedialog.askopenfilename(title='Select .localization file',
                                               filetypes=[('Localization', '*.localization'), ('All', '*.*')])
        if not loc: return
        csv = self.filedialog.asksaveasfilename(title='Save CSV', defaultextension='.csv',
                                                 filetypes=[('CSV', '*.csv')])
        if not csv: return
        success, output = Backend.run_loc_export(self.current_game.get(), loc, csv)
        self._log(f'\n--- Export CSV ---')
        self._log(output)
        self.status_text.set('✅ CSV exported' if success else '❌ Export failed')

    def _import_csv(self):
        g = GAMES[self.current_game.get()]
        if g['wip']:
            self.messagebox.showwarning('WIP', 'Spider-Man 2 loc-import is not ready yet.')
            return

        loc = self.filedialog.askopenfilename(title='Select original .localization file',
                                               filetypes=[('Localization', '*.localization'), ('All', '*.*')])
        if not loc: return
        csv = self.filedialog.askopenfilename(title='Select translated CSV',
                                               filetypes=[('CSV', '*.csv')])
        if not csv: return
        out = self.filedialog.asksaveasfilename(title='Save modified .loc', defaultextension='.loc',
                                                 filetypes=[('LOC', '*.loc'), ('All', '*.*')])
        if not out: return
        success, output = Backend.run_loc_import(self.current_game.get(), loc, csv, out)
        self._log(f'\n--- Import CSV ---')
        self._log(output)
        self.status_text.set('✅ Loc imported' if success else '❌ Import failed')

    def _patch_loc(self):
        if not self._ensure_paths(): return
        g = GAMES[self.current_game.get()]
        if g['wip']:
            self.messagebox.showwarning('WIP', 'Spider-Man 2 patch is not ready yet.')
            return
        loc = self.filedialog.askopenfilename(title='Select modified .loc file',
                                               filetypes=[('LOC', '*.loc'), ('All', '*.*')])
        if not loc: return
        slot = self.slot_index.get()
        self._run_cmd([
            '--toc', self.toc_path.get(),
            '--hashdb', g['hashdb'],
            'patch',
            '--archive-dir', self.archive_dir.get(),
            '--files', f"{g['loc_hash']}={loc}",
            '--asset-index', slot,
            '--output-toc', self.toc_path.get() + '.new',
            '--no-backup',
        ], f'Patch Loc slot {slot} ({g["name"]})')

    def _patch_both(self):
        if not self._ensure_paths(): return
        g = GAMES[self.current_game.get()]
        if g['wip']:
            self.messagebox.showwarning('WIP', 'Spider-Man 2 patch is not ready yet.')
            return
        loc = self.filedialog.askopenfilename(title='Select modified .loc file',
                                               filetypes=[('LOC', '*.loc'), ('All', '*.*')])
        if not loc: return
        font = self.filedialog.askopenfilename(title='Select font file',
                                                filetypes=[('Font', '*.gfx;*.ttf;*.otf'), ('All', '*.*')])
        if not font: return
        slot = self.slot_index.get()
        self._run_cmd([
            '--toc', self.toc_path.get(),
            '--hashdb', g['hashdb'],
            'patch',
            '--archive-dir', self.archive_dir.get(),
            '--files', f"{g['loc_hash']}={loc}",
                       f"{g['font_hash']}={font}",
            '--asset-index', slot,
            '--output-toc', self.toc_path.get() + '.new',
            '--no-backup',
        ], f'Patch Loc+Font slot {slot} ({g["name"]}')"

    def _toc_info(self):
        if not self._ensure_paths(): return
        g = GAMES[self.current_game.get()]
        self._run_cmd([
            '--toc', self.toc_path.get(),
            '--hashdb', g['hashdb'],
            'info',
        ], f'TOC Info ({g["name"]})')

    def run(self):
        self.root.mainloop()


# ─── CLI ──────────────────────────────────────────────────────────────────────
def cli_main():
    p = argparse.ArgumentParser(prog='sm_tool', description='Unified Spider-Man Asset Tool')
    p.add_argument('--game', choices=list(GAMES.keys()), default='smr',
                   help='Game version (default: smr)')
    p.add_argument('--gui', action='store_true', help='Launch GUI (default if no command)')

    # Only parse --game and --gui; everything else passes through to backend
    args, remaining = p.parse_known_args()

    if args.gui or not remaining:
        gui = SpiderToolGUI()
        gui.run()
        return

    # CLI mode: route to backend
    game = GAMES[args.game]
    mod_name = game['module']

    # Use remaining args from parse_known_args — argparse will pass through
    backend_args = remaining

    # Auto-insert hashdb if not in args
    has_hashdb = any(a == '--hashdb' or a.startswith('--hashdb=') for a in backend_args)
    if not has_hashdb and game.get('hashdb'):
        backend_args = ['--hashdb', game['hashdb']] + backend_args

    old_argv = sys.argv
    sys.argv = [mod_name] + backend_args

    try:
        if mod_name == 'sm1':
            from sm1 import main; main()
        elif mod_name == 'mm':
            from mm import main; main()
        elif mod_name == 'smr':
            from smr import main; main()
        elif mod_name == 'sm2':
            from sm2 import main; main()
    finally:
        sys.argv = old_argv


if __name__ == '__main__':
    cli_main()
