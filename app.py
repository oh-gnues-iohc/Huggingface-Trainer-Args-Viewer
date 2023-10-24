from srcs.finder import DataclassFinder
from pprint import pprint
# 사용 예시
if __name__ == "__main__":
    file_path = "sample.py"  # 대상 파일 경로 설정
    # finder.find_dataclasses()
    
    for dataclass in DataclassFinder(file_path):
        pprint(dataclass)
