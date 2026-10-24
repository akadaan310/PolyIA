"""Push an exact committed snapshot with a short-lived Sites credential on stdin.

Fallback for this environment's missing Sites source-workflow executable.
Never writes or prints the credential; native Sites tools still own publication.
"""
import json
import os
import subprocess
import sys
import termios
from urllib.parse import urlparse

terminal_state = None
if sys.stdin.isatty():
    terminal_state = termios.tcgetattr(sys.stdin)
    hidden_state = termios.tcgetattr(sys.stdin)
    hidden_state[3] &= ~termios.ECHO
    termios.tcsetattr(sys.stdin, termios.TCSANOW, hidden_state)
print('Ready for Sites credential JSON on stdin (input is hidden).', flush=True)
try:
    credential = json.loads(sys.stdin.readline())
finally:
    if terminal_state is not None:
        termios.tcsetattr(sys.stdin, termios.TCSANOW, terminal_state)

if credential.get('auth_mode') != 'http_extra_header':
    raise SystemExit('Unsupported Sites authentication mode')
remote = credential['remote_url']
if urlparse(remote).scheme != 'https' or urlparse(remote).hostname != 'git.chatgpt-team.site':
    raise SystemExit('Unexpected source repository host')
branch = credential['branch']
if not branch or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_-.' for c in branch):
    raise SystemExit('Invalid source branch')
process_env = os.environ.copy()
for key in list(process_env):
    if key.startswith('GIT_TRACE') or key == 'GIT_CURL_VERBOSE':
        del process_env[key]
process_env['GIT_CONFIG_COUNT'] = '1'
process_env['GIT_CONFIG_KEY_0'] = f'http.{remote}.extraheader'
process_env['GIT_CONFIG_VALUE_0'] = 'Authorization: Bearer ' + credential['token']
credential.clear()
result = subprocess.run(['git', 'push', remote, f'HEAD:refs/heads/{branch}'], env=process_env, text=True, capture_output=True)
if result.returncode:
    # Git errors contain the credential-free remote; request tracing is disabled.
    print(result.stderr.strip())
    raise SystemExit(result.returncode)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
observed = subprocess.check_output(['git', 'ls-remote', remote, f'refs/heads/{branch}'], env=process_env, text=True).split()[0]
if observed != head:
    raise SystemExit('Pushed source readback mismatch')
print(json.dumps({'commit_sha': head, 'remote_head': observed, 'branch': branch, 'verified': True}))
