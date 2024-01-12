import asyncio
import difflib
import shlex
import sys
from typing import Tuple

async def lines_difference(file1, file2):
    with open(file1) as f1:
        lines1 = f1.readlines()
        lines1 = [line.rstrip("\n") for line in lines1]
    with open(file2) as f2:
        lines2 = f2.readlines()
        lines2 = [line.rstrip("\n") for line in lines2]
    diff = difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm="", n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == "+"]
    removed = [line[1:] for line in lines if line[0] == "-"]
    additions = [i for i in added if i not in removed]
    removedt = [i for i in removed if i not in added]
    return additions, removedt

async def run_command(cmd: str) -> Tuple[str, str, int, int]:
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

async def update_requirements(main, test):
    additions, removed = await lines_difference(main, test)
    try:
        for requirement in additions:
            await run_command(f"pip install {requirement}")
            print(f">> Installed Requirement: {requirement}")
    except Exception as e:
        print(f"Error installing requirements: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <main_requirements.txt> <test_requirements.txt>")
        sys.exit(1)
    
    asyncio.run(update_requirements(sys.argv[1], sys.argv[2]))
