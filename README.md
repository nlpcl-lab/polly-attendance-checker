# 과제 코드 작동 여부 테스팅 툴

## Requirements
Python 3 이상, Ubuntu 혹은 Mac 환경에서 정상적으로 작동합니다.
```bash
pip install tqdm
```

## 사용법
1. `unzip-all.sh`, `code_work_tester.py`, `auto_grade.py` 파일을 홈워크 파일들과 동일한 경로에 옮깁니다.

2. `sh unzip-all.sh` 명령어로 혹시 남아있는 압축파일들을 풀어줍니다.

3. `python code_work_tester.py --multi <멀티프로세스 개수>` 명령어로 모든 py 파일들을 실행시킵니다.

4. 각 학번별로 생성된 폴더를 확인합니다. stdout.txt는 실행 중 print된 데이터의 모음, stderr.txt는 실행 중 기록된 에러의 모음입니다. csv파일만을 출력한 코드의 경우에는 stdout이 비어있을 가능성이 있습니다. stderr가 있다 -> 코드가 제대로 안 돌아갈 가능성이 있다고 보시면 됩니다.

5. `python auto_grade.py` 명령어로 stderr파일들의 요약을 확인합니다. 결과는 `student_stats.csv`에 있습니다.

6. ImportError의 경우, 해당 라이브러리들을 환경에 설치한 후에 3~5번 과정을 다시 진행합니다.

7. `code_work_tester.py`와 `auto_grade.py`의 경우 `--dir` argument를 이용하여, 같은 폴더가 아니어도 채점을 진행할 수 있습니다.

## HW#5
```bash
python assign5_tester.py --gold_tsv gap-test.tsv --multi 8 --input_dir example --output_dir data
```

After first execution:
```bash
python assign5_tester.py --gold_tsv gap-test.tsv --multi 8 --input_dir example --output_dir data --cache
```