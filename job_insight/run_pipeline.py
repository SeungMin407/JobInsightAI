import subprocess

subprocess.run(["python", "crawler.py"])
subprocess.run(["python", "detail_crawler.py"])
subprocess.run(["python", "embedding_ranker.py"])
subprocess.run(["python", "analyzer.py"])

print("전체 분석 완료")