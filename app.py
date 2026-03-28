import streamlit as st
from supabase import create_client, Client
import random

# 수파베이스 연결 (secrets.toml에서 정보 가져오기)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("👨‍🏫 자산배분 게임 관리자 대시보드")
st.write("학생 명단을 입력하고 그룹을 무작위로 배정합니다.")

# 1. 명단 입력창
student_list_text = st.text_area("학생 명단을 붙여넣으세요 (엔터로 구분)", height=200)

# 2. 배정 및 DB 저장 버튼
if st.button("명단 등록 및 A/B 그룹 배정 시작"):
    if not student_list_text.strip():
        st.warning("명단을 입력해주세요.")
    else:
        # 빈 줄을 제외하고 이름 리스트 생성
        names = [name.strip() for name in student_list_text.split('\n') if name.strip()]
        
        # 리스트 무작위 섞기
        random.shuffle(names)
        
        # 절반으로 나누기
        mid = len(names) // 2
        group_a = names[:mid]
        group_b = names[mid:]
        
        # 수파베이스에 넣을 데이터 형태(딕셔너리 리스트)로 가공
        insert_data = []
        for name in group_a:
            insert_data.append({"name": name, "group_tag": "A"})
        for name in group_b:
            insert_data.append({"name": name, "group_tag": "B"})
            
        # 수파베이스에 데이터 전송
        try:
            # 만약 기존에 테스트했던 명단이 있다면 모두 지우고 초기화
            supabase.table("asset_allocation_player").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
            # 새 명단 데이터 삽입
            supabase.table("asset_allocation_player").insert(insert_data).execute()
            
            st.success(f"총 {len(names)}명 등록 완료! (A그룹: {len(group_a)}명, B그룹: {len(group_b)}명)")
            
            # 확인용 표 출력
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("A그룹 (분기별 확인)")
                st.write(group_a)
            with col2:
                st.subheader("B그룹 (연간 확인)")
                st.write(group_b)
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.info("중복된 이름이 있거나 데이터베이스 연결 문제일 수 있습니다.")