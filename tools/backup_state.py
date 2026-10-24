#!/usr/bin/env python3
"""A consistent SQLite backup; never overwrite a destination or create a source."""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3

def backup(source,destination):
    source=Path(source).resolve(strict=True);destination=Path(destination).absolute()
    if not source.is_file():raise ValueError('Source must be an existing ledger file')
    if destination.exists():raise FileExistsError('Destination already exists; choose a new backup name')
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
    try:
        # URI mode=ro prevents a mistaken path from creating a new empty source.
        from urllib.parse import quote
        with closing(sqlite3.connect('file:'+quote(str(source),safe='/')+'?mode=ro',uri=True,timeout=15)) as src:
            with closing(sqlite3.connect(str(destination))) as dst:
                src.backup(dst,pages=128)
                status=dst.execute('PRAGMA integrity_check').fetchone()[0]
                if status!='ok':raise ValueError('Backup SQLite integrity check failed: '+status)
        raw=destination.read_bytes()
        return {'ok':True,'destination':str(destination),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                'next':'Verify the application event chain and compare its head/checkpoint with an independently retained receipt before restore.'}
    except BaseException:
        # An incomplete newly created destination cannot be mistaken for a good backup.
        if destination.exists():destination.unlink()
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('destination');a=p.parse_args()
    print(json.dumps(backup(a.source,a.destination),indent=2))
