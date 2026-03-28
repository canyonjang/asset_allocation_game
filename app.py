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
# 2. 화면 분기 (학생용 vs 교수님용)
# ---------------------------------------------------------
st.sidebar.title("모드 선택")
app_mode = st.sidebar.radio("접속할 화면을 선택하세요", ["🙋‍♂️ 학생 로그인", "👨‍🏫 교수님 대시보드"])

if app_mode == "🙋‍♂️ 학생 로그인":
    st.title("📊 자산배분 게임")
    
    if 'user_data' not in st.session_state:
        st.info("교수님이 안내해주신 자신의 이름을 입력하고 입장해주세요.")
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
        user_res = supabase.table("asset_allocation_player").select("*").eq("id", st.session_state['user_data']['id']).execute()
        user = user_res.data[0]
        st.session_state['user_data'] = user
        
        st.write(f"**👤 참여자:** {user['name']} | **현재 자산:** {user['balance']:,.0f}원")
        
        # --- [13단계: 학생 최종 화면] ---
        if current_phase == 13:
            st.balloons()
            st.header("🏆 3년간의 투자가 모두 종료되었습니다!")
            
            initial_balance = 1000000
            final_balance = user['balance']
            cum_return = ((final_balance / initial_balance) - 1) * 100
            ann_return = ((final_balance / initial_balance) ** (1/3) - 1) * 100
            
            st.write(f"최종 자산은 **{final_balance:,.0f}원** 입니다.")
            st.info(f"📈 **누적 수익률:** {cum_return:.1f}%\n\n📊 **연 평균 수익률:** {ann_return:.1f}%")
            
            if user['group_tag'] == 'B':
                total_quizzes = len(quizzes)
                quiz_score = user.get('quiz_score') or 0
                st.success(f"🎯 **K-POP 퀴즈 결과:** 총 {total_quizzes}개 중 **{quiz_score}개** 정답!")
                
            st.write("전체 결과는 교수님 화면을 주목해주세요.")
            
        elif current_phase == 0:
            st.warning("⏳ 아직 게임이 시작되지 않았습니다. 교수님의 지시를 기다려주세요.")
            if st.button("🔄 교수님이 시작했다고 하시면 누르세요!"):
                st.rerun()
            
        elif current_phase > 0:
            st.subheader(f"📅 현재 시점: {market_data[current_phase]['label']}")
            
            if st.button("🔄 다음 단계 새로고침 (교수님 지시 후 클릭)"):
                st.rerun()
            st.divider()
            
            submit_key = f"submit_{current_phase}"
            if submit_key not in st.session_state:
                st.session_state[submit_key] = False

            # --- [A그룹: 매 분기 수익률 확인 및 잦은 변경 유도] ---
            if user['group_tag'] == 'A':
                st.write(f"📉 이번 분기 주식 수익률: **{market_data[current_phase]['stock']}%**")
                st.write(f"📈 이번 분기 채권 수익률: **{market_data[current_phase]['bond']}%**")
                
                if st.session_state[submit_key] or user.get('last_completed_phase') == current_phase:
                    st.success("✅ 비중 확정이 완료되었습니다. 대기해주세요.")
                else:
                    new_stock_ratio = st.slider("다음 분기를 위한 '주식' 투자 비중을 결정하세요 (%)", 0, 100, int(user['stock_ratio']*100))
                    if st.button("비중 확정 및 제출"):
                        supabase.table("asset_allocation_player").update({
                            "stock_ratio": new_stock_ratio / 100.0,
                            "last_completed_phase": current_phase
                        }).eq("id", user['id']).execute()
                        st.session_state[submit_key] = True
                        st.rerun()
                        
            # --- [B그룹: 분기 중 퀴즈 / 매년 말 성과 확인] ---
            elif user['group_tag'] == 'B':
                if current_phase % 4 != 0: 
                    quiz = quizzes.get(current_phase)
                    
                    if st.session_state[submit_key] or user.get('last_completed_phase') == current_phase:
                        res_state = st.session_state.get(f"quiz_result_{current_phase}")
                        if res_state == "correct":
                            st.success("✅ 정답입니다! 훌륭해요 🎉")
                        elif res_state == "incorrect":
                            ans = quiz['ans'] if quiz else ""
                            st.error(f"❌ 오답입니다. (정답: {ans})")
                        st.info("✅ 퀴즈 제출이 완료되었습니다. 대기해주세요.")
                        
                    elif quiz:
                        st.write(f"**💡 Q. {quiz['q']}**")
                        answer = st.radio("정답을 선택하세요:", quiz['options'], key=f"q_{current_phase}")
                        if st.button("퀴즈 제출"):
                            is_correct = (answer == quiz['ans'])
                            st.session_state[f"quiz_result_{current_phase}"] = "correct" if is_correct else "incorrect"
                            
                            current_score = user.get('quiz_score') or 0
                            update_data = {"last_completed_phase": current_phase}
                            if is_correct:
                                update_data["quiz_score"] = current_score + 1
                                
                            supabase.table("asset_allocation_player").update(update_data).eq("id", user['id']).execute()
                            st.session_state[submit_key] = True
                            st.rerun()
                else: 
                    st.write("📊 **1년간의 투자 성과가 도착했습니다!**")
                    
                    start_p = current_phase - 3
                    stock_cum, bond_cum = 1.0, 1.0
                    for p in range(start_p, current_phase + 1):
                        stock_cum *= (1 + market_data[p]["stock"] / 100.0)
                        bond_cum *= (1 + market_data[p]["bond"] / 100.0)
                    annual_stock_ret = (stock_cum - 1) * 100
                    annual_bond_ret = (bond_cum - 1) * 100
                    
                    st.info(f"📈 지난 1년간 누적 주식 수익률: **{annual_stock_ret:.1f}%**")
                    st.info(f"📉 지난 1년간 누적 채권 수익률: **{annual_bond_ret:.1f}%**")
                    
                    if st.session_state[submit_key] or user.get('last_completed_phase') == current_phase:
                        st.success("✅ 비중 확정이 완료되었습니다. 대기해주세요.")
                    else:
                        new_stock_ratio = st.slider("내년을 위한 '주식' 투자 비중을 결정하세요 (%)", 0, 100, int(user['stock_ratio']*100))
                        if st.button("비중 확정 및 제출"):
                            supabase.table("asset_allocation_player").update({
                                "stock_ratio": new_stock_ratio / 100.0,
                                "last_completed_phase": current_phase
                            }).eq("id", user['id']).execute()
                            st.session_state[submit_key] = True
                            st.rerun()

# ---------------------------------------------------------
# 3. 교수님 대시보드 화면
# ---------------------------------------------------------
elif app_mode == "👨‍🏫 교수님 대시보드":
    st.title("👨‍🏫 관리자 대시보드 및 게임 통제")
    
    if 'admin_auth' not in st.session_state:
        st.session_state['admin_auth'] = False

    if not st.session_state['admin_auth']:
        st.info("교수님 전용 페이지입니다. 비밀번호를 입력해주세요.")
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
        
        # --- [학생 제출 현황 모니터링] ---
        if 0 < current_phase < 13:
            st.subheader("✅ 현재 단계 완료 현황 (퀴즈 & 자산조정)")
            players_data = supabase.table("asset_allocation_player").select("last_completed_phase").execute().data
            total_stu = len(players_data)
            completed_stu = sum(1 for p in players_data if p.get("last_completed_phase") == current_phase)
            
            col_m1, col_m2 = st.columns([3, 1])
            with col_m1:
                st.metric("제출 완료 학생", f"{completed_stu}명 / {total_stu}명")
                if total_stu > 0:
                    st.progress(completed_stu / total_stu)
            with col_m2:
                if st.button("🔄 현황 새로고침"):
                    st.rerun()
            st.divider()
        
        # --- [다음 단계 진행 로직] ---
        if current_phase < 13:
            if st.button(f"⏩ {current_phase + 1}단계로 진행 (시장 수익률 일괄 적용)"):
                new_phase = current_phase + 1
                
                if new_phase <= 12:
                    stock_ret = market_data[new_phase]["stock"] / 100.0
                    bond_ret = market_data[new_phase]["bond"] / 100.0
                    
                    players = supabase.table("asset_allocation_player").select("*").execute().data
                    for p in players:
                        s_ratio = p['stock_ratio']
                        b_ratio = 1.0 - s_ratio
                        new_balance = p['balance'] * (s_ratio * (1 + stock_ret) + b_ratio * (1 + bond_ret))
                        supabase.table("asset_allocation_player").update({"balance": new_balance}).eq("id", p['id']).execute()
                        
                supabase.table("asset_allocation_game_state").update({"current_phase": new_phase}).eq("id", 1).execute()
                st.success(f"{new_phase}단계로 넘어갔습니다. 학생들에게 새로고침을 누르라고 안내해주세요.")
                st.rerun()
                
        # --- [최종 결과 분석 화면] ---
        if current_phase == 13:
            st.header("📈 주식 프리미엄 퍼즐 분석 결과")
            st.write("결과가 도출되었습니다. 성과를 자주 확인한 그룹(A)과 장기 투자 그룹(B)의 차이를 확인하세요.")
            
            players = supabase.table("asset_allocation_player").select("*").execute().data
            df = pd.DataFrame(players)
            
            # 그룹별 평균 계산
            avg_balance = df.groupby('group_tag')['balance'].mean().reset_index()
            val_a = avg_balance[avg_balance['group_tag']=='A']['balance'].values[0] if not avg_balance[avg_balance['group_tag']=='A'].empty else 0
            val_b = avg_balance[avg_balance['group_tag']=='B']['balance'].values[0] if not avg_balance[avg_balance['group_tag']=='B'].empty else 0
            
            cum_ret_a = ((val_a / 1000000) - 1) * 100 if val_a else 0
            ann_ret_a = ((val_a / 1000000) ** (1/3) - 1) * 100 if val_a else 0
            cum_ret_b = ((val_b / 1000000) - 1) * 100 if val_b else 0
            ann_ret_b = ((val_b / 1000000) ** (1/3) - 1) * 100 if val_b else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("A그룹 (근시안) 평균 자산", f"{val_a:,.0f}원")
                st.info(f"📉 **평균 누적 수익률:** {cum_ret_a:.1f}%\n\n📊 **평균 연 수익률:** {ann_ret_a:.1f}%")
            with col2:
                st.metric("B그룹 (장기) 평균 자산", f"{val_b:,.0f}원")
                st.info(f"📈 **평균 누적 수익률:** {cum_ret_b:.1f}%\n\n📊 **평균 연 수익률:** {ann_ret_b:.1f}%")
                
            st.bar_chart(avg_balance.set_index('group_tag'))
            
            st.divider()
            st.subheader("🏅 전체 학생 수익률 랭킹")
            
            # 개인별 누적 수익률 계산 및 정렬
            df['cum_return'] = ((df['balance'] / 1000000) - 1) * 100
            df_sorted = df.sort_values(by='cum_return', ascending=False).reset_index(drop=True)
            
            # 화면 출력용 데이터 프레임 가공
            df_display = df_sorted[['name', 'group_tag', 'cum_return', 'balance']].copy()
            df_display.index = df_display.index + 1 # 1등부터 시작
            df_display.columns = ['이름', '소속 그룹', '누적 수익률(%)', '최종 자산(원)']
            df_display['누적 수익률(%)'] = df_display['누적 수익률(%)'].apply(lambda x: f"{x:.1f}%")
            df_display['최종 자산(원)'] = df_display['최종 자산(원)'].apply(lambda x: f"{int(x):,}")
            
            st.dataframe(df_display, use_container_width=True)
            
        st.divider()
        st.subheader("⚙️ 게임 초기화 및 학생 명단 관리")
        if st.button("🔄 게임 초기화 (시작 전으로 되돌리기 및 자산 리셋)"):
            supabase.table("asset_allocation_game_state").update({"current_phase": 0}).eq("id", 1).execute()
            supabase.table("asset_allocation_player").update({
                "balance": 1000000, 
                "stock_ratio": 0.5,
                "last_completed_phase": 0,
                "quiz_score": 0
            }).neq("id", "00000000-0000-0000-0000-000000000000").execute()
            st.warning("게임이 0단계로 초기화되고 모든 학생의 자산이 100만 원으로 복구되었습니다.")
            st.rerun()
            
        student_list_text = st.text_area("새로운 학생 명단을 붙여넣으세요 (엔터로 구분 / 기존 데이터는 삭제됩니다)", height=100)
        if st.button("새 명단 등록 및 A/B 그룹 배정 시작"):
            if not student_list_text.strip():
                st.warning("명단을 입력해주세요.")
            else:
                names = [name.strip() for name in student_list_text.split('\n') if name.strip()]
                random.shuffle(names)
                mid = len(names) // 2
                group_a = names[:mid]
                group_b = names[mid:]
                
                insert_data = []
                for name in group_a:
                    insert_data.append({"name": name, "group_tag": "A", "balance": 1000000, "stock_ratio": 0.5, "last_completed_phase": 0, "quiz_score": 0})
                for name in group_b:
                    insert_data.append({"name": name, "group_tag": "B", "balance": 1000000, "stock_ratio": 0.5, "last_completed_phase": 0, "quiz_score": 0})
                    
                try:
                    supabase.table("asset_allocation_player").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                    supabase.table("asset_allocation_player").insert(insert_data).execute()
                    st.success(f"총 {len(names)}명 등록 완료! (A그룹: {len(group_a)}명, B그룹: {len(group_b)}명)")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
