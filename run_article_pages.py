#!/usr/bin/env python3
"""
생성된 뉴스 기사 Streamlit 페이지 실행 도구
"""

import os
import sys
import subprocess
import glob
from datetime import datetime

def list_available_articles():
    """사용 가능한 기사 목록 표시"""
    
    articles_dir = "streamlit_articles"
    
    if not os.path.exists(articles_dir):
        print("❌ streamlit_articles 디렉토리가 없습니다.")
        return []
    
    # 기사 파일들 찾기
    article_files = glob.glob(os.path.join(articles_dir, "article_*.py"))
    
    if not article_files:
        print("❌ 생성된 기사가 없습니다.")
        return []
    
    # 파일명으로 정렬 (최신순)
    article_files.sort(reverse=True)
    
    print("📰 생성된 뉴스 기사 목록:")
    print("=" * 60)
    
    articles_info = []
    
    for i, file_path in enumerate(article_files, 1):
        filename = os.path.basename(file_path)
        
        # 파일명에서 정보 추출
        parts = filename.replace("article_", "").replace(".py", "").split("_")
        
        if len(parts) >= 3:
            symbol = parts[0]
            date_part = parts[1]
            time_part = parts[2]
            
            # 날짜 시간 포맷팅
            try:
                dt = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = f"{date_part} {time_part}"
            
            print(f"   {i:2d}. {symbol:8s} | {formatted_time} | {filename}")
            articles_info.append({
                'index': i,
                'symbol': symbol,
                'filename': filename,
                'filepath': file_path,
                'time': formatted_time
            })
        else:
            print(f"   {i:2d}. {filename}")
            articles_info.append({
                'index': i,
                'symbol': 'Unknown',
                'filename': filename,
                'filepath': file_path,
                'time': 'Unknown'
            })
    
    print("=" * 60)
    return articles_info

def run_streamlit_article(filepath, port=8501):
    """특정 기사의 Streamlit 페이지 실행"""
    
    try:
        print(f"🚀 Streamlit 페이지 실행 중...")
        print(f"📄 파일: {filepath}")
        print(f"🌐 URL: http://localhost:{port}")
        print(f"⏹️  중지하려면 Ctrl+C를 누르세요")
        print("-" * 60)
        
        # Streamlit 실행
        cmd = ["streamlit", "run", filepath, "--server.port", str(port)]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n✅ Streamlit 서버가 중지되었습니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

def run_latest_article():
    """가장 최근 기사 실행"""
    
    articles = list_available_articles()
    
    if not articles:
        return
    
    latest_article = articles[0]
    print(f"\n🔥 가장 최근 기사를 실행합니다:")
    print(f"   📈 {latest_article['symbol']} | {latest_article['time']}")
    
    run_streamlit_article(latest_article['filepath'])

def run_selected_article():
    """사용자가 선택한 기사 실행"""
    
    articles = list_available_articles()
    
    if not articles:
        return
    
    print(f"\n실행할 기사 번호를 선택하세요 (1-{len(articles)}):")
    
    try:
        choice = input("선택 (번호 입력): ").strip()
        
        if not choice:
            print("❌ 선택이 취소되었습니다.")
            return
        
        choice_num = int(choice)
        
        if 1 <= choice_num <= len(articles):
            selected_article = articles[choice_num - 1]
            print(f"\n🎯 선택된 기사:")
            print(f"   📈 {selected_article['symbol']} | {selected_article['time']}")
            
            run_streamlit_article(selected_article['filepath'])
        else:
            print(f"❌ 잘못된 번호입니다. 1-{len(articles)} 사이의 번호를 입력하세요.")
            
    except ValueError:
        print("❌ 올바른 번호를 입력하세요.")
    except KeyboardInterrupt:
        print("\n❌ 선택이 취소되었습니다.")

def run_multiple_articles():
    """여러 기사를 다른 포트에서 실행"""
    
    articles = list_available_articles()
    
    if not articles:
        return
    
    print(f"\n동시에 실행할 기사들을 선택하세요 (예: 1,3,5 또는 1-3):")
    
    try:
        choice = input("선택 (쉼표로 구분): ").strip()
        
        if not choice:
            print("❌ 선택이 취소되었습니다.")
            return
        
        # 선택된 번호들 파싱
        selected_indices = []
        
        for part in choice.split(','):
            part = part.strip()
            if '-' in part:
                # 범위 선택 (예: 1-3)
                start, end = map(int, part.split('-'))
                selected_indices.extend(range(start, end + 1))
            else:
                # 개별 선택
                selected_indices.append(int(part))
        
        # 중복 제거 및 정렬
        selected_indices = sorted(list(set(selected_indices)))
        
        # 유효성 검사
        valid_indices = [i for i in selected_indices if 1 <= i <= len(articles)]
        
        if not valid_indices:
            print("❌ 유효한 번호가 없습니다.")
            return
        
        print(f"\n🚀 {len(valid_indices)}개 기사를 동시 실행합니다:")
        
        processes = []
        base_port = 8501
        
        for i, article_idx in enumerate(valid_indices):
            article = articles[article_idx - 1]
            port = base_port + i
            
            print(f"   📈 {article['symbol']} | Port {port} | {article['time']}")
            
            # 백그라운드에서 실행
            cmd = ["streamlit", "run", article['filepath'], "--server.port", str(port)]
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append((process, port, article['symbol']))
        
        print(f"\n🌐 접속 URL:")
        for process, port, symbol in processes:
            print(f"   📊 {symbol}: http://localhost:{port}")
        
        print(f"\n⏹️  모든 서버를 중지하려면 Ctrl+C를 누르세요")
        
        try:
            # 모든 프로세스가 종료될 때까지 대기
            for process, port, symbol in processes:
                process.wait()
        except KeyboardInterrupt:
            print(f"\n🛑 모든 Streamlit 서버를 중지합니다...")
            for process, port, symbol in processes:
                process.terminate()
            print("✅ 모든 서버가 중지되었습니다.")
            
    except ValueError:
        print("❌ 올바른 형식으로 입력하세요. (예: 1,3,5 또는 1-3)")
    except KeyboardInterrupt:
        print("\n❌ 선택이 취소되었습니다.")

def main():
    """메인 함수"""
    
    print("📰 뉴스 기사 Streamlit 페이지 실행 도구")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # 명령줄 인수가 있는 경우
        if sys.argv[1] == "latest":
            run_latest_article()
            return
        elif sys.argv[1] == "list":
            list_available_articles()
            return
    
    # 대화형 메뉴
    while True:
        print("\n실행 옵션을 선택하세요:")
        print("1. 🔥 가장 최근 기사 실행")
        print("2. 📋 기사 목록에서 선택")
        print("3. 🚀 여러 기사 동시 실행")
        print("4. 📄 기사 목록만 보기")
        print("5. ❌ 종료")
        
        try:
            choice = input("\n선택 (1-5): ").strip()
            
            if choice == "1":
                run_latest_article()
                break
            elif choice == "2":
                run_selected_article()
                break
            elif choice == "3":
                run_multiple_articles()
                break
            elif choice == "4":
                list_available_articles()
            elif choice == "5":
                print("👋 종료합니다.")
                break
            else:
                print("❌ 1-5 사이의 번호를 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n👋 종료합니다.")
            break

if __name__ == "__main__":
    main()
