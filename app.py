import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="日給計算ツール", layout="centered")

st.title("ジョインバイト日給＋交通費計算")

# 業務区分の定義
JOB_OPTIONS = {
    "① 会場整理・グッズ販売・ステージハンド等 (時給1,300/5h保障)": 1,
    "② ステージ搬入・搬出 (時給1,500/3h保障)": 2,
    "③ ライブハウス搬入搬出 (時給1,500/3h保障)": 3,
    "④ チラシ配布・サンプリング等 (時給1,300)": 4,
    "⑤ EXシアタードリンク業務 (時給1,300)": 5,
    "⑥ 東京グローブ座 (時給1,300)": 6,
    "⑦ ケータリング・ランナー (時給1,420/5h保障)": 7,
}

# 交通費一覧（2026年4月9日改定版）
LOCATION_OPTIONS = {
    "その他（下記以外の都内会場・一般）: ¥800": 800,
    "【東京都】お台場周辺 (Zepp DiverCity / TOYOTA ARENA等): ¥1,100": 1100,
    "【東京都】有明周辺 (ガーデンシアター / アリーナ / 豊洲PIT等): ¥1,100": 1100,
    "【東京都】Zepp Haneda: ¥1,100": 1100,
    "【東京都】アリーナ立川立飛: ¥1,240": 1240,
    "【東京都】J:COMホール八王子: ¥820": 820,
    "【埼玉県】さいたまスーパーアリーナ: ¥1,060": 1060,
    "【埼玉県】ベルーナドーム（西武ドーム）: ¥1,100": 1100,
    "【埼玉県】大宮ソニック: ¥1,060": 1060,
    "【埼玉県】三郷市文化会館: ¥1,440": 1440,
    "【神奈川県】神奈川県民ホール / 横浜BUNTAI: ¥1,300": 1300,
    "【神奈川県】パシフィコ横浜 / ぴあアリーナMM: ¥1,300": 1300,
    "【神奈川県】Kアリーナ横浜 / KT Zepp Yokohama: ¥1,300": 1300,
    "【神奈川県】横浜アリーナ: ¥1,100": 1100,
    "【神奈川県】日産スタジアム: ¥1,200": 1200,
    "【神奈川県】よこすか芸術劇場: ¥1,760": 1760,
    "【神奈川県】ラゾーナ川崎 / SUPERNOVA KAWASAKI: ¥880": 880,
    "【千葉県】幕張メッセ: ¥1,400": 1400,
    "【千葉県】LaLa arena TOKYO-BAY: ¥1,300": 1300,
    "【千葉県】千葉県文化会館: ¥1,820": 1820,
    "【千葉県】市川市文化会館: ¥800": 800,
    "【千葉県】市原市市民会館: ¥2,600": 2600,
    "【千葉県】千葉スタジオ: ¥2,820": 2820,
}

# 1. 業務・時間の入力
st.subheader("1. 業務内容と時間の選択")
selected_job_label = st.selectbox("業務内容", list(JOB_OPTIONS.keys()))
job_type = JOB_OPTIONS[selected_job_label]

col1, col2 = st.columns(2)
with col1:
    start_time = st.time_input("開始時間", value=datetime.strptime("09:00", "%H:%M").time())
with col2:
    end_time = st.time_input("終了時間", value=datetime.strptime("18:00", "%H:%M").time())

# 2. 会場（交通費）の選択
st.subheader("2. 勤務会場の選択")
selected_loc_label = st.selectbox("勤務会場 / エリア", list(LOCATION_OPTIONS.keys()))
transport_fee = LOCATION_OPTIONS[selected_loc_label]

def calculate_wage(job_type, start_t, end_t):
    start_dt = datetime.combine(datetime.today(), start_t)
    end_dt = datetime.combine(datetime.today(), end_t)
    
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
        
    work_hours = (end_dt - start_dt).total_seconds() / 3600.0
    
    if work_hours <= 0:
        return None, "勤務時間が0以下です"

    rates = {1: 1300, 2: 1500, 3: 1500, 4: 1300, 5: 1300, 6: 1300, 7: 1420}
    base_rate = rates[job_type]
    
    if job_type in [1, 7]:
        guaranteed_h = 5.0
        base_wage = base_rate * 5.0
    elif job_type in [2, 3]:
        guaranteed_h = 3.0
        base_wage = 5000.0 if job_type == 2 else 4500.0
    elif job_type == 4:
        if work_hours <= 3.0:
            guaranteed_h, base_wage = 3.0, 3900.0
        elif work_hours <= 4.0:
            guaranteed_h, base_wage = 4.0, 5200.0
        else:
            guaranteed_h, base_wage = 5.0, 6500.0
    elif job_type == 5:
        if work_hours <= 3.0:
            guaranteed_h, base_wage = 3.0, 4000.0
        elif work_hours <= 3.5:
            guaranteed_h, base_wage = 3.5, 4550.0
        elif work_hours <= 4.5:
            guaranteed_h, base_wage = 4.5, 5850.0
        else:
            guaranteed_h, base_wage = 5.0, 6500.0
    elif job_type == 6:
        if work_hours <= 3.5:
            guaranteed_h, base_wage = 3.5, 5300.0
        elif work_hours <= 4.5:
            guaranteed_h, base_wage = 4.5, 5850.0
        else:
            guaranteed_h, base_wage = 5.0, 6500.0

    # 15分刻みで残業(8h超)・深夜(22-5時)を判定
    extra_wage = 0.0
    curr = start_dt
    accumulated_h = 0.0
    step = timedelta(minutes=15)
    
    while curr < end_dt:
        is_night = (curr.hour >= 22 or curr.hour < 5)
        is_overtime = (accumulated_h >= 8.0)
        
        if accumulated_h >= guaranteed_h:
            step_wage = base_rate / 4.0
            if is_overtime:
                step_wage += (base_rate * 0.25) / 4.0
            if is_night:
                step_wage += (base_rate * 0.25) / 4.0
            extra_wage += step_wage
            
        accumulated_h += 0.25
        curr += step

    wage_pay = int(round(base_wage + extra_wage))
    return work_hours, wage_pay

st.markdown("---")
if st.button("日給を計算する", type="primary"):
    hours, wage_pay = calculate_wage(job_type, start_time, end_time)
    if hours is None:
        st.error(wage_pay)
    else:
        total_payment = wage_pay + transport_fee
        
        st.metric(label="勤務時間（全拘束時間）", value=f"{hours:.2f} 時間")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(label="給料本体", value=f"¥{wage_pay:,}")
        with col_b:
            st.metric(label="交通費手当", value=f"¥{transport_fee:,}")
            
        st.subheader(f"合計支給額: **¥{total_payment:,}**")