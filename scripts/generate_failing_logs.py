import json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CASES=ROOT/'benchmark'/'cases'
def main():
    for c in sorted(p for p in CASES.iterdir() if p.is_dir()):
        m=json.loads((c/'metadata.json').read_text()); repo=c/'repo'; target=m['targeted_test']
        env=os.environ.copy(); env['PYTHONPATH']=str(repo)
        p=subprocess.run([sys.executable,'-m','pytest','-q',target],cwd=repo,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
        (c/'failing_log.txt').write_text(f'$ python -m pytest -q {target}\n\n{p.stdout}\n[exit_code={p.returncode}]\n')
        if p.returncode==0: raise RuntimeError(f'{c.name}: targeted test unexpectedly passed')
        print(f'{c.name}: failure reproduced and log written.')
if __name__=='__main__': main()
