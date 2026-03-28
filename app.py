import streamlit as st
from supabase import create_client, Client
import random

# ---------------------------------------------------------
# 1. 수파베이스 연결 및 데이터 세팅
# ---------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 실제 2020년(코로나 쇼크 및 회복) 기반 수익률 데이터 (단위: %)
market_data = {
    1: {"stock": -20.0, "bond": 1.0, "label": "1년차 1분기"},
    2: {"stock": 20.0, "bond": 0.5, "label": "1년차 2분기"},
    3: {"stock": 8.5, "bond": 0.2, "label": "1년차 3분기"},
    4: {"stock": 11.7, "bond": -0.5, "label": "1년차 4분기 (연말 결산)"}
    # 필요시 5~12분기 데이터를 계속 추가할 수 있습니다.
}

# B그룹을 위한 K-POP 퀴즈 (분기별 1개)
quizzes = {
    1: {"q": "BTS의 데뷔 곡은 무엇일까요?", "options": ["No More Dream", "Fire", "Butter"], "ans": "No More Dream"},
    2: {"q": "블랙핑크 멤버 중 솔로 곡 'LALISA'를 발표한 멤버는?", "options": ["제니", "리사", "로제"], "ans": "리사"},
    3: {"q": "BTS의 팬덤 이름은 무엇일까요?", "options": ["BLINK", "ARMY", "MIDZY"], "ans": "ARMY"}
}

# 현재 게임 단계 불러오기 함수
def get_current_phase():
    res = supabase.table("asset_allocation_game_state").select("current_phase").eq("id", 1).execute()
    return res.data[0]['current_phase'] if res.data else 0

current_phase = get_current_phase()

# ---------------------------------------------------------
# 2. 화면 분기 (학생용 vs 선생님용)
# ---------------------------------------------------------
st.sidebar.title("모드 선택")
app_mode = st.sidebar.radio("접속할 화면을 선택하세요", ["🙋‍♂️ 학생 로그인", "👨‍🏫 선생님 대시보드"])

if app_mode == "🙋‍♂️ 학생 로그인":
    st.title("📊 자산배분 게임")
    
    # 세션에 로그인 정보가 없으면 로그인 창 표시
    if 'user_data' not in st.session_state:
        st.info("선생님이 안내해주신 자신의 이름을 입력하고 입장해주세요.")
        student_name = st.text_input("이름 입력:")
        if st.button("로그인"):
            res = supabase.table("asset_allocation_player").select("*").eq("name", student_name).execute()
            if res.data:
                st.session_state['user_data'] = res.data[0]
                st.success(f"{student_name}님 환영합니다!")
                st.rerun()
            else:
                st.error("명단에 이름이 없습니다. 정확히 입력했는지 확인해주세요.")
                
    # 로그인 성공 후 화면
    else:
        user = st.session_state['user_data']
        st.write(f"**👤 참여자:** {user['name']} | **현재 자산:** {user['balance']:,.0f}원")
        
        if current_phase == 0:
            st.warning("⏳ 아직 게임이 시작되지 않았습니다. 선생님의 지시를 기다려주세요.")
            
        elif current_phase > 0:
            st.subheader(f"📅 현재 시점: {market_data[current_phase]['label']}")
            
            # --- [A그룹: 매 분기 확인 및 비중 조정] ---
            if user['group_tag'] == 'A':
                st.write(f"📉 이번 분기 주식 수익률: **{market_data[current_phase]['stock']}%**")
                st.write(f"📈 이번 분기 채권 수익률: **{market_data[current_phase]['bond']}%**")
                
                new_stock_ratio = st.slider("다음 분기를 위한 '주식' 투자 비중을 결정하세요 (%)", 0, 100, int(user['stock_ratio']*100))
                if st.button("비중 확정 및 제출"):
                    # 실제 앱에서는 여기서 DB에 비중을 업데이트하고 계산하는 로직이 들어갑니다.
                    st.success("제출 완료! 다음 분기를 기다려주세요.")
                    
            # --- [B그룹: 1~3분기는 퀴즈, 4분기는 연말 정산] ---
            elif user['group_tag'] == 'B':
                if current_phase % 4 != 0: # 1, 2, 3분기 (연말이 아닐 때)
                    st.info("운용팀에서 자산을 굴리는 중입니다. 대기 시간 동안 퀴즈를 풀어보세요!")
                    quiz = quizzes.get(current_phase)
                    if quiz:
                        st.write(f"**💡 Q. {quiz['q']}**")
                        answer = st.radio("정답을 선택하세요:", quiz['options'])
                        if st.button("퀴즈 제출"):
                            if answer == quiz['ans']:
                                st.success("정답입니다! 훌륭해요 🎉")
                            else:
                                st.error(f"오답입니다. 정답은 '{quiz['ans']}' 입니다.")
                else: # 4분기 (연말 결산)
                    st.write("📊 **1년간의 투자 성과가 도착했습니다!**")
                    # (실제로는 1~4분기 누적 수익률을 계산해서 보여줌)
                    st.write("1년간 묵혀둔 주식이 크게 반등했습니다!") 
                    new_stock_ratio = st.slider("내년을 위한 '주식' 투자 비중을 결정하세요 (%)", 0, 100, int(user['stock_ratio']*100))
                    if st.button("비중 확정 및 제출"):
                        st.success("제출 완료! 내년도 결과를 기다려주세요.")

elif app_mode == "👨‍🏫 선생님 대시보드":
    # (여기에 비밀번호 입력 로직을 추가하여 학생들의 접근을 막을 수 있습니다)
    st.title("👨‍🏫 관리자 대시보드 및 게임 통제")
    
    st.write(f"**현재 진행 단계:** {current_phase}단계 (0=시작 전)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏩ 다음 분기로 진행"):
            new_phase = current_phase + 1
            supabase.table("asset_allocation_game_state").update({"current_phase": new_phase}).eq("id", 1).execute()
            st.success(f"{new_phase}단계로 넘어갔습니다. 학생들에게 화면을 새로고침하라고 안내해주세요.")
    with col2:
        if st.button("🔄 게임 초기화 (시작 전으로)"):
            supabase.table("asset_allocation_game_state").update({"current_phase": 0}).eq("id", 1).execute()
            st.warning("게임이 0단계로 초기화되었습니다.")
            
    # 아래에 이전 단계에서 만든 [명단 등록 및 그룹 배정] 코드를 그대로 두시면 됩니다.
    st.divider()
    st.subheader("👥 학생 명단 세팅 (최초 1회만)")
    # ... (이전에 만든 명단 등록 코드) ...
