import streamlit as st
from supabase import create_client, Client
import random
import pandas as pd

# ---------------------------------------------------------
# 1. 수파베이스 연결 및 데이터 세팅
# ---------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 12분기(3년) 수익률 시나리오
# 주식: 변동성이 크지만 장기 우상향 / 채권: 잃지 않고 매 분기 1.0~1.5%의 안정적 수익
market_data = {
    1: {"stock": -20.0, "bond": 1.2, "label": "1년차 1분기 (시장 급락)"},
    2: {"stock": 20.0, "bond": 1.0, "label": "1년차 2분기 (강한 반등)"},
    3: {"stock": 8.5, "bond": 1.5, "label": "1년차 3분기"},
    4: {"stock": 11.7, "bond": 1.1, "label": "1년차 4분기 (연말 결산)"},
    5: {"stock": 5.0, "bond": 1.4, "label": "2년차 1분기"},
    6: {"stock": -4.0, "bond": 1.2, "label": "2년차 2분기 (단기 조정)"},
    7: {"stock": 6.0, "bond": 1.3, "label": "2년차 3분기"},
    8: {"stock": 2.0, "bond": 1.5, "label": "2년차 4분기 (연말 결산)"},
    9: {"stock": -8.0, "bond": 1.1, "label": "3년차 1분기 (인플레이션 우려)"},
    10: {"stock": 3.0, "bond": 1.4, "label": "3년차 2분기"},
    11: {"stock": -5.0, "bond": 1.2, "label": "3년차 3분기"},
    12: {"stock": 4.0, "bond": 1.5, "label": "3년차 4분기 (최종 결산)"}
}

# B그룹을 위한 분기별 K-POP 퀴즈 (매년 4분기는 결산이므로 제외)
quizzes = {
    1: {"q": "BTS의 데뷔 곡은 무엇일까요?", "options": ["No More Dream", "Fire", "Butter"], "ans": "No More Dream"},
    2: {"q": "블랙핑크 멤버 중 솔로 곡 'LALISA'를 발표한 멤버는?", "options": ["제니", "리사", "로제"], "ans": "리사"},
    3: {"q": "뉴진스(NewJeans)의 데뷔 앨범 타이틀곡 중 하나인 것은?", "options": ["Ditto", "Hype Boy", "OMG"], "ans": "Hype Boy"},
    5: {"q": "아이브(IVE)의 멤버가 아닌 사람은?", "options": ["장원영", "안유진", "카리나"], "ans": "카리나"},
    6: {"q": "르세라핌(LE SSERAFIM)의 그룹명은 'IM FEARLESS'의 애너그램이다.", "options": ["O", "X"], "ans": "O"},
    7: {"q": "에스파(aespa)의 세계관 속 아바타를 부르는 용어는?", "options": ["ae", "navis", "mamba"], "ans": "ae"},
    9: {"q": "세븐틴(SEVENTEEN)의 멤버 수는?", "options": ["13명", "15명", "17명"], "ans": "13명"},
    10: {"q": "블랙핑크의 공식 팬덤명은?", "options": ["ARMY", "BLINK", "MIDZY"], "ans": "BLINK"},
    11: {"q": "방탄소년단(BTS)의 소속사 하이브의 예전 이름은?", "options": ["SM", "JYP", "빅히트"], "ans": "빅히트"}
}

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
                
    else:
        # DB에서 최신 유저 정보를 매번 다시 불러옴 (자산 업데이트 반영)
        user_res = supabase.table("asset_allocation_player").select("*").eq("id", st.session_state['user_data']['id']).execute()
        user = user_res.data[0]
        st.session_state['user_data'] = user
        
        st.write(f"**👤 참여자:** {user['name']} | **현재 자산:** {user['balance']:,.0f}원")
        
        # [게임 종료: 결과 확인]
        if current_phase == 13:
            st.balloons()
            st.header("🏆 3년간의 투자가 모두 종료되었습니다!")
            st.write(f"최종 자산은 **{user['balance']:,.0f}원** 입니다. 전체 결과는 선생님 화면을 주목해주세요.")
            
        elif current_phase == 0:
            st.warning("⏳ 아직 게임이 시작되지 않았습니다. 선생님의 지시를 기다려주세요.")
            if st.button("🔄 선생님이 시작했다고 하시면 누르세요!"):
                st.rerun()
            
        elif current_phase > 0:
            st.subheader(f"📅 현재 시점: {market_data[current_phase]['label']}")
            
            # --- [새로고침 버튼: 단계 전환용] ---
            if st.button("🔄 다음 단계 새로고침 (선생님 지시 후 클릭)"):
                st.rerun()
            st.divider()
            
            # 중복 제출 방지용 상태 키
            submit_key = f"submit_{current_phase}"
            if submit_key not in st.session_state:
                st.session_state[submit_key] = False

            # --- [A그룹: 매 분기 수익률 확인 및 잦은 변경 유도] ---
            if user['group_tag'] == 'A':
                st.write(f"📉 이번 분기 주식 수익률: **{market_data[current_phase]['stock']}%**")
                st.write(f"📈 이번 분기 채권 수익률: **{market_data[current_phase]['bond']}%**")
                
                if st.session_state[submit_key]:
                    st.success("✅ 비중 확정이 완료되었습니다. 대기해주세요.")
                else:
                    new_stock_ratio = st.slider("다음 분기를 위한 '주식' 투자 비중을 결정하세요 (%)", 0, 100, int(user['stock_ratio']*100))
                    if st.button("비중 확정 및 제출"):
                        supabase.table("asset_allocation_player").update({"stock_ratio": new_stock_ratio / 100.0}).eq("id", user['id']).execute()
                        st.session_state[submit_key] = True
                        st.rerun()
                        
            # --- [B그룹: 분기 중 퀴즈 / 매년 말 성과 확인] ---
            elif user['group_tag'] == 'B':
                if current_phase % 4 != 0: 
                    st.info("자산 운용팀에서 장기적 관점으로 자산을 굴리는 중입니다. 대기 시간 동안 퀴즈를 풀어보세요!")
                    quiz = quizzes.get(current_phase)
                    if quiz:
                        st.write(f"**💡 Q. {quiz['q']}**")
                        answer = st.radio("정답을 선택하세요:", quiz['options'], key=f"q_{current_phase}")
                        if st.button("퀴즈 제출"):
                            if answer == quiz['ans']:
                                st.success("정답입니다! 훌륭해요 🎉")
                            else:
                                st.error(f"오답입니다. 정답은 '{quiz['ans']}' 입니다.")
                else: 
                    st.write("📊 **1년간의 투자 성과가 도착했습니다!**")
                    if st.session_state[submit_key]:
                        st.success("✅ 비중 확정이 완료되었습니다. 대기해주세요.")
                    else:
                        new_stock_ratio = st.slider("내년을 위한 '주식' 투자 비중을 결정하세요 (%)", 0, 100, int(user['stock_ratio']*100))
                        if st.button("비중 확정 및 제출"):
                            supabase.table("asset_allocation_player").update({"stock_ratio": new_stock_ratio / 100.0}).eq("id", user['id']).execute()
                            st.session_state[submit_key] = True
                            st.rerun()

# ---------------------------------------------------------
# 3. 선생님 대시보드 화면
# ---------------------------------------------------------
elif app_mode == "👨‍🏫 선생님 대시보드":
    st.title("👨‍🏫 관리자 대시보드 및 게임 통제")
    
    if 'admin_auth' not in st.session_state:
        st.session_state['admin_auth'] = False

    if not st.session_state['admin_auth']:
        st.info("선생님 전용 페이지입니다. 비밀번호를 입력해주세요.")
        pw_input = st.text_input("비밀번호", type="password") 
        if st.button("입장"):
            if pw_input == "3383":
                st.session_state['admin_auth'] = True
                st.rerun() 
            else:
                st.error("비밀번호가 일치하지 않습니다.")
                
    else:
        st.success("인증되었습니다.")
        if st.button("🔒 로그아웃"):
            st.session_state['admin_auth'] = False
            st.rerun()
            
        st.divider()
        st.write(f"### **현재 진행 단계:** {current_phase}단계 (13 = 최종 결과)")
        
        # --- [다음 단계 진행 및 수익률 계산 로직] ---
        if current_phase < 13:
            if st.button(f"⏩ {current_phase + 1}단계로 진행 (시장 수익률 일괄 적용)"):
                new_phase = current_phase + 1
                
                # 학생 자산 업데이트 계산식 적용
                if new_phase <= 12:
                    stock_ret = market_data[new_phase]["stock"] / 100.0
                    bond_ret = market_data[new_phase]["bond"] / 100.0
                    
                    players = supabase.table("asset_allocation_player").select("*").execute().data
                    for p in players:
                        s_ratio = p['stock_ratio']
                        b_ratio = 1.0 - s_ratio
                        new_balance = p['balance'] * (s_ratio * (1 + stock_ret) + b_ratio * (1 + bond_ret))
                        supabase.table("asset_allocation_player").update({"balance": new_balance}).eq("id", p['id']).execute()
                        
                # DB 상태 업데이트
                supabase.table("asset_allocation_game_state").update({"current_phase": new_phase}).eq("id", 1).execute()
                st.success(f"{new_phase}단계로 넘어갔습니다. 학생들에게 새로고침을 누르라고 안내해주세요.")
                st.rerun()
                
        # --- [최종 결과 분석 화면] ---
        if current_phase == 13:
            st.header("📈 주식 프리미엄 퍼즐 분석 결과")
            st.write("결과가 도출되었습니다. 성과를 자주 확인한 그룹(A)과 장기 투자 그룹(B)의 차이를 확인하세요.")
            
            players = supabase.table("asset_allocation_player").select("*").execute().data
            df = pd.DataFrame(players)
            
            avg_balance = df.groupby('group_tag')['balance'].mean().reset_index()
            avg_balance['balance'] = avg_balance['balance'].astype(int)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("A그룹 (근시안) 평균 자산", f"{avg_balance[avg_balance['group_tag']=='A']['balance'].values[0]:,.0f}원")
            with col2:
                st.metric("B그룹 (장기) 평균 자산", f"{avg_balance[avg_balance['group_tag']=='B']['balance'].values[0]:,.0f}원")
                
            st.bar_chart(avg_balance.set_index('group_tag'))
            
            st.info("""
            **💡 수업 포인트:**
            A그룹은 1분기 폭락장(-20%)에서 고통을 느끼고 주식 비중을 낮춰, 이후의 V자 반등 혜택을 온전히 누리지 못했습니다. 
            반면 1년 단위로 확인한 B그룹은 단기 소음에 휘둘리지 않고 주식의 높은 프리미엄을 획득했습니다. 이것이 인간의 '자기통제'와 관련된 근시안적 손실회피(MLA)입니다.
            """)
            
        st.divider()
        if st.button("🔄 게임 초기화 (시작 전으로 되돌리기 및 자산 리셋)"):
            supabase.table("asset_allocation_game_state").update({"current_phase": 0}).eq("id", 1).execute()
            supabase.table("asset_allocation_player").update({"balance": 1000000, "stock_ratio": 0.5}).neq("id", "00000000-0000-0000-0000-000000000000").execute()
            st.warning("게임이 0단계로 초기화되고 모든 학생의 자산이 100만 원으로 복구되었습니다.")
            st.rerun()
