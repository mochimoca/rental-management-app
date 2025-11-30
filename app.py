import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


# ================================================
# 🔐 Google Sheets 読み込み関数（完成版）
# ================================================
def load_sheet(sheet_url, sheet_name):

    # --- Streamlit の secrets.toml に保存したサービスアカウント ---
    service_account_info = st.secrets["gcp_service_account"]

    # --- 必要なスコープ（編集権限も含む） ---
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # --- 認証 ---
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes
    )

    # --- gspread のクライアント作成 ---
    gc = gspread.authorize(credentials)

    # --- スプレッドシートをURLで開く ---
    sh = gc.open_by_url(sheet_url)

    # --- シート名でワークシート取得 ---
    worksheet = sh.worksheet(sheet_name)

    # --- DataFrame に変換 ---
    df = pd.DataFrame(worksheet.get_all_records())

    return df



# ================================================
# 📄 list シート読み込み処理
# ================================================
LIST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hIToCx1ICTuIv9qA8PNx_y9R3xI-7cjWarr-5XOfGxg"

st.header("📄 ゆらぎマスタ（list）読み込みテスト")

try:
    list_df = load_sheet(LIST_SHEET_URL, "list")
    st.success("list シートの読み込みに成功しました！")
    st.dataframe(list_df)
except Exception as e:
    st.error("list シートの読み込みに失敗しました。")
    st.error("👇エラー内容（これをそのまま教えてね）")
    st.exception(e)



# ================================================
# 🏡 レンタル管理アプリ（テスト版）
# ================================================
st.title("🏡 アパート・マンション レンタル管理アプリ（動作テスト版）")
st.subheader("--- 物件情報と収支管理 ---")

# --- ダミーデータ（後で削除OK） ---
data = {
    '物件名': ['Aハイツ', 'Bマンション', 'Cコーポ', 'Dハイツ'],
    '家賃': [75000, 120000, 55000, 90000],
    '修繕費': [5000, 10000, 3000, 8000],
    '入居者名': ['田中', '佐藤', '山本', '伊藤'],
    '入居開始日': ['2023-04-01', '2022-11-15', '2024-01-01', '2023-07-20'],
    '空室': [False, False, False, True]
}

df = pd.DataFrame(data)
df['入居開始日'] = pd.to_datetime(df['入居開始日'])

# --- フィルタリング ---
st.sidebar.header('フィルタリング')

show_empty = st.sidebar.checkbox('空室のみ表示', value=False)
filtered_df = df[df['空室']] if show_empty else df.copy()

st.sidebar.subheader('家賃範囲')
min_rent = int(df['家賃'].min())
max_rent = int(df['家賃'].max())

rent_range = st.sidebar.slider(
    '選択する家賃の範囲',
    min_rent,
    max_rent,
    (min_rent, max_rent)
)

filtered_df = filtered_df[
    (filtered_df['家賃'] >= rent_range[0]) &
    (filtered_df['家賃'] <= rent_range[1])
]

# --- 表示 ---
st.header("📋 フィルタ後の物件一覧")
st.dataframe(filtered_df)

# --- 収益分析 ---
st.header("📊 収益分析")
total_revenue = filtered_df['家賃'].sum()
total_maintenance = filtered_df['修繕費'].sum()
net_profit = total_revenue - total_maintenance

col1, col2, col3 = st.columns(3)
col1.metric("総家賃収入", f"¥{total_revenue:,}")
col2.metric("総修繕費", f"¥{total_maintenance:,}")
col3.metric("純利益", f"¥{net_profit:,}")

# --- グラフ ---
st.header("📈 物件別家賃比較")
chart_data = filtered_df[['物件名', '家賃']]
st.bar_chart(chart_data, x='物件名', y='家賃')
